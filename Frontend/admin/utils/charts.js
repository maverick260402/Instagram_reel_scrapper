/**
 * Chart Helper Utilities
 * Handles Chart.js configuration and creation
 */

const ChartHelper = {
    // Chart colors matching the purple theme
    colors: {
        purple: '#8b5cf6',
        purpleLight: '#a78bfa',
        purpleDark: '#7c3aed',
        success: '#10b981',
        error: '#ef4444',
        warning: '#f59e0b',
        gray: '#9ca3af',
        white: '#ffffff'
    },

    // Default chart configuration
    defaultConfig: {
        responsive: true,
        maintainAspectRatio: true,
        plugins: {
            legend: {
                labels: {
                    color: '#ffffff',
                    font: {
                        family: 'Inter'
                    }
                }
            }
        },
        scales: {
            x: {
                ticks: {
                    color: '#9ca3af',
                    font: {
                        family: 'Inter'
                    }
                },
                grid: {
                    color: '#262626'
                }
            },
            y: {
                ticks: {
                    color: '#9ca3af',
                    font: {
                        family: 'Inter'
                    }
                },
                grid: {
                    color: '#262626'
                }
            }
        }
    },

    /**
     * Create line chart for daily trends
     */
    createDailyTrendChart(canvasId, labels, reelsData, usersData) {
        const ctx = document.getElementById(canvasId).getContext('2d');

        return new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Reels Scraped',
                        data: reelsData,
                        borderColor: this.colors.purple,
                        backgroundColor: 'rgba(139, 92, 246, 0.1)',
                        tension: 0.4,
                        fill: true,
                        yAxisID: 'y'
                    },
                    {
                        label: 'Active Users',
                        data: usersData,
                        borderColor: this.colors.success,
                        backgroundColor: 'rgba(16, 185, 129, 0.1)',
                        tension: 0.4,
                        fill: true,
                        yAxisID: 'y1'
                    }
                ]
            },
            options: {
                ...this.defaultConfig,
                scales: {
                    y: {
                        type: 'linear',
                        display: true,
                        position: 'left',
                        ticks: {
                            color: this.colors.purple,
                            font: { family: 'Inter' }
                        },
                        grid: { color: '#262626' }
                    },
                    y1: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        ticks: {
                            color: this.colors.success,
                            font: { family: 'Inter' }
                        },
                        grid: { drawOnChartArea: false }
                    },
                    x: {
                        ticks: {
                            color: '#9ca3af',
                            font: { family: 'Inter' }
                        },
                        grid: { color: '#262626' }
                    }
                }
            }
        });
    },

    /**
     * Create bar chart for credit usage
     */
    createCreditUsageChart(canvasId, labels, data) {
        const ctx = document.getElementById(canvasId).getContext('2d');

        return new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Credits Used',
                    data: data,
                    backgroundColor: this.colors.purple,
                    borderColor: this.colors.purpleLight,
                    borderWidth: 1
                }]
            },
            options: {
                ...this.defaultConfig,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            color: '#9ca3af',
                            font: { family: 'Inter' }
                        },
                        grid: { color: '#262626' }
                    },
                    x: {
                        ticks: {
                            color: '#9ca3af',
                            font: { family: 'Inter' }
                        },
                        grid: { color: '#262626' }
                    }
                }
            }
        });
    },

    /**
     * Create pie chart for account distribution
     */
    createAccountUsageChart(canvasId, labels, data) {
        const ctx = document.getElementById(canvasId).getContext('2d');

        return new Chart(ctx, {
            type: 'pie',
            data: {
                labels: labels,
                datasets: [{
                    data: data,
                    backgroundColor: [
                        this.colors.purple,
                        this.colors.purpleLight,
                        this.colors.purpleDark,
                        this.colors.success,
                        this.colors.warning
                    ],
                    borderColor: '#141414',
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            color: '#ffffff',
                            font: { family: 'Inter' },
                            padding: 15
                        }
                    }
                }
            }
        });
    },

    /**
     * Create donut chart for success/failure rates
     */
    createSuccessFailureChart(canvasId, successCount, failureCount) {
        const ctx = document.getElementById(canvasId).getContext('2d');

        return new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Success', 'Failure'],
                datasets: [{
                    data: [successCount, failureCount],
                    backgroundColor: [this.colors.success, this.colors.error],
                    borderColor: '#141414',
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            color: '#ffffff',
                            font: { family: 'Inter' },
                            padding: 15
                        }
                    }
                }
            }
        });
    },

    /**
     * Create bar chart for hourly usage pattern
     */
    createHourlyUsageChart(canvasId, hours, reelCounts) {
        const ctx = document.getElementById(canvasId).getContext('2d');

        const labels = hours.map(h => `${h}:00`);

        return new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Reels Scraped',
                    data: reelCounts,
                    backgroundColor: this.colors.purple,
                    borderColor: this.colors.purpleLight,
                    borderWidth: 1
                }]
            },
            options: {
                ...this.defaultConfig,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            color: '#9ca3af',
                            font: { family: 'Inter' }
                        },
                        grid: { color: '#262626' }
                    },
                    x: {
                        ticks: {
                            color: '#9ca3af',
                            font: { family: 'Inter' },
                            maxRotation: 45,
                            minRotation: 45
                        },
                        grid: { color: '#262626' }
                    }
                }
            }
        });
    },

    /**
     * Destroy a chart instance
     */
    destroyChart(chartInstance) {
        if (chartInstance) {
            chartInstance.destroy();
        }
    }
};
