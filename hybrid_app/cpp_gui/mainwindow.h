#pragma once

#include <QMainWindow>
#include <QPushButton>
#include <QTabWidget>
#include <QProcess>
#include <QPlainTextEdit>
#include <QtCharts/QChartView>
#include <QtCharts/QChart>
#include <QtCharts/QLineSeries>
#include <QtCharts/QValueAxis>

QT_BEGIN_NAMESPACE
namespace Ui { class MainWindow; }
QT_END_NAMESPACE

class MainWindow : public QMainWindow {
    Q_OBJECT
public:
    explicit MainWindow(QWidget *parent = nullptr);
    ~MainWindow();

private slots:
    void startSimulation();
    void stopSimulation();
    void readSimOutput();
    void setupChartAxes(QChart *chart, QLineSeries *series, const QString &xLabel, const QString &yLabel);

private:
    // Main tab widget
    QTabWidget *mainTabs;

    // Sim tab widgets
    QWidget *simTab;
    QPushButton *startSimButton;
    QPushButton *stopSimButton;
    QTabWidget *simPlotTabs;

    // Three charts for voltage, current, resistance
    QChartView *voltageChartView;
    QChartView *currentChartView;
    QChartView *resistanceChartView;

    QChart *voltageChart;
    QChart *currentChart;
    QChart *resistanceChart;

    QLineSeries *voltageSeries;
    QLineSeries *currentSeries;
    QLineSeries *resistanceSeries;

    QProcess *simProcess;
};