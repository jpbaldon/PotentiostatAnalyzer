#include "mainwindow.h"
#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QJsonDocument>
#include <QJsonObject>
#include <QValueAxis>
#include <QDebug>
#include <QDir>

MainWindow::MainWindow(QWidget *parent) : QMainWindow(parent), simProcess(new QProcess(this)) {
    // Main tabs
    mainTabs = new QTabWidget(this);
    setWindowTitle("Potentiostat Data Analyzer in C++/Qt/Python");
    setCentralWidget(mainTabs);
    setGeometry(100, 100, 800, 700);

    // ----- SIM TAB -----
    simTab = new QWidget(this);
    QVBoxLayout *simLayout = new QVBoxLayout(simTab);

    // Buttons start/stop
    QHBoxLayout *btnLayout = new QHBoxLayout();
    startSimButton = new QPushButton("Start Simulation", this);
    stopSimButton = new QPushButton("Stop Simulation", this);
    stopSimButton->setEnabled(false);
    btnLayout->addWidget(startSimButton);
    btnLayout->addWidget(stopSimButton);
    simLayout->addLayout(btnLayout);

    // Sub-tabs for plots
    simPlotTabs = new QTabWidget(this);

    // Create charts and series
    voltageSeries = new QLineSeries();
    currentSeries = new QLineSeries();
    resistanceSeries = new QLineSeries();

    voltageChart = new QChart();
    voltageChart->legend()->hide();
    voltageChart->addSeries(voltageSeries);
    voltageChart->setTitle("Voltage");
    setupChartAxes(voltageChart, voltageSeries, "Time (s)", "Voltage (V)");

    currentChart = new QChart();
    currentChart->legend()->hide();
    currentChart->addSeries(currentSeries);
    currentChart->setTitle("Current");
    setupChartAxes(currentChart, currentSeries, "Time (s)", "Current (A)");

    resistanceChart = new QChart();
    resistanceChart->legend()->hide();
    resistanceChart->addSeries(resistanceSeries);
    resistanceChart->setTitle("Resistance");
    setupChartAxes(resistanceChart, resistanceSeries, "Time (s)", "Resistance (Ω)");

    voltageChartView = new QChartView(voltageChart);
    currentChartView = new QChartView(currentChart);
    resistanceChartView = new QChartView(resistanceChart);

    simPlotTabs->addTab(voltageChartView, "Voltage");
    simPlotTabs->addTab(currentChartView, "Current");
    simPlotTabs->addTab(resistanceChartView, "Resistance");

    simLayout->addWidget(simPlotTabs);

    mainTabs->addTab(simTab, "Live Simulation");

    // Connect signals
    connect(startSimButton, &QPushButton::clicked, this, &MainWindow::startSimulation);
    connect(stopSimButton, &QPushButton::clicked, this, &MainWindow::stopSimulation);
    connect(simProcess, &QProcess::readyReadStandardOutput, this, &MainWindow::readSimOutput);
    connect(simProcess, &QProcess::readyReadStandardError, this, [this]() {
        QByteArray err = simProcess->readAllStandardError();
        qDebug() << "Sim error:" << err;
    });
}

MainWindow::~MainWindow() {
    if (simProcess->state() == QProcess::Running) {
        simProcess->kill();
        simProcess->waitForFinished();
    }
}

// Starts simulation process
void MainWindow::startSimulation() {
    voltageSeries->clear();
    currentSeries->clear();
    resistanceSeries->clear();

    QString exePath = QCoreApplication::applicationDirPath() + "/simulate.exe";

    simProcess->start(exePath);

    if (!simProcess->waitForStarted()) {
        qWarning() << "Failed to start simulation";
        return;
    }
    startSimButton->setEnabled(false);
    stopSimButton->setEnabled(true);
}

// Stops simulation process
void MainWindow::stopSimulation() {
    if (simProcess->state() == QProcess::Running) {
        simProcess->terminate();
        simProcess->waitForFinished(3000);
    }
    startSimButton->setEnabled(true);
    stopSimButton->setEnabled(false);
}

// Read output JSON line from simulation and update plots
void MainWindow::readSimOutput() {
    while (simProcess->canReadLine()) {
        QByteArray line = simProcess->readLine().trimmed();
        if (line.isEmpty()) continue;

        QJsonParseError parseError;
        QJsonDocument doc = QJsonDocument::fromJson(line, &parseError);
        if (parseError.error != QJsonParseError::NoError) {
            qWarning() << "JSON parse error:" << parseError.errorString();
            continue;
        }
        QJsonObject obj = doc.object();

        // Expected JSON keys: time, voltage, current, resistance
        double time = obj["time"].toDouble();
        double voltage = obj["voltage"].toDouble();
        double current = obj["current"].toDouble();
        double resistance = obj["resistance"].toDouble();

        voltageSeries->append(time, voltage);
        currentSeries->append(time, current);
        resistanceSeries->append(time, resistance);

        // Scroll X axis if needed (similar to previous example)
        auto updateAxis = [&](QChart *chart, QLineSeries *series){
            QValueAxis *axisX = qobject_cast<QValueAxis*>(chart->axisX());
            if (!axisX) return;
            if (time > axisX->max()) {
                axisX->setMax(time + 1);
                axisX->setMin(axisX->min() + 1);
            }
        };
        updateAxis(voltageChart, voltageSeries);
        updateAxis(currentChart, currentSeries);
        updateAxis(resistanceChart, resistanceSeries);

        auto updateAxisRange = [](QChart *chart, QLineSeries *series) {
            if (series->count() < 2) return;

            QValueAxis *axisX = qobject_cast<QValueAxis *>(chart->axes(Qt::Horizontal).first());
            QValueAxis *axisY = qobject_cast<QValueAxis *>(chart->axes(Qt::Vertical).first());
            if (!axisX || !axisY) return;

            // X-axis range (rounded)
            qreal minX = series->at(0).x();
            qreal maxX = series->at(series->count() - 1).x();
            axisX->setRange(std::floor(minX), std::ceil(maxX));
            axisX->setTickCount(6);

            // Y-axis range (dynamic and safe)
            qreal minY = series->at(0).y();
            qreal maxY = minY;
            for (const QPointF &point : series->points()) {
                minY = std::min(minY, point.y());
                maxY = std::max(maxY, point.y());
            }

            // Add margin that's proportional to the range (but never too big)
            qreal range = maxY - minY;
            qreal margin = (range < 1e-6) ? 0.01 : 0.1 * range;  // avoid collapsing to 0

            qreal newMinY = minY - margin;
            qreal newMaxY = maxY + margin;

            // Avoid negative values if range is positive-only (e.g., for current)
            if (newMinY >= 0 && minY >= 0) newMinY = 0;

            axisY->setRange(newMinY, newMaxY);
            axisY->setTickCount(6);
        };

        // Call for each chart
        updateAxisRange(voltageChart, voltageSeries);
        updateAxisRange(currentChart, currentSeries);
        updateAxisRange(resistanceChart, resistanceSeries);
    }
}

void MainWindow::setupChartAxes(QChart *chart, QLineSeries *series, const QString &xLabel, const QString &yLabel) {

    chart->legend()->hide();

    QValueAxis *xAxis = new QValueAxis();
    xAxis->setRange(0, 1);
    xAxis->setTitleText(xLabel);
    xAxis->setLabelFormat("%.2f");

    QValueAxis *yAxis = new QValueAxis();
    yAxis->setRange(0, 1);
    yAxis->setTitleText(yLabel);
    yAxis->setLabelFormat("%.2f");

    chart->addAxis(xAxis, Qt::AlignBottom);
    chart->addAxis(yAxis, Qt::AlignLeft);

    series->attachAxis(xAxis);
    series->attachAxis(yAxis);
}