import React from 'react';
import { Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

// We need to register the components we want to use with Chart.js
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

function ExpenditureChart({ analysisData }) {
  // The component receives the expenditure analysis data as a prop

  // 1. Prepare the data for the chart
  // Chart.js expects labels and datasets in a specific format.
  const chartData = {
    labels: Object.keys(analysisData.spend_by_category), // The category names (e.g., "Shopping", "Dining")
    datasets: [
      {
        label: 'Spend by Category ($)',
        data: Object.values(analysisData.spend_by_category), // The amount spent in each category
        backgroundColor: 'rgba(52, 152, 219, 0.6)', // A nice blue color for the bars
        borderColor: 'rgba(52, 152, 219, 1)',
        borderWidth: 1,
      },
    ],
  };

  // 2. Configure the chart's options (e.g., title, responsiveness)
  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: 'Expenditure by Category',
        font: {
          size: 18,
        },
      },
    },
    scales: {
        y: {
            beginAtZero: true,
            title: {
                display: true,
                text: 'Amount ($)'
            }
        }
    }
  };

  // 3. Render the Bar chart component
  return (
    <div className="chart-container">
      <Bar options={chartOptions} data={chartData} />
    </div>
  );
}

export default ExpenditureChart;