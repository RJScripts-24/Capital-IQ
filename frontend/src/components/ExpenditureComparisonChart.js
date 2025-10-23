import React, { forwardRef } from 'react';
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

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

const ExpenditureComparisonChart = forwardRef(function ExpenditureComparisonChart({ analysisData }, ref) {
  const categories = Object.keys(analysisData.spend_by_category || {});
  const currentValues = categories.map((c) => analysisData.spend_by_category[c] || 0);
  const plannedValues = categories.map((c) => (analysisData.savings_plan && analysisData.savings_plan[c]) ? (analysisData.spend_by_category[c] * 0.85) : (analysisData.spend_by_category[c] || 0));

  const data = {
    labels: categories,
    datasets: [
      {
        label: 'Current ($)',
        data: currentValues,
        backgroundColor: 'rgba(52, 152, 219, 0.6)',
        borderColor: 'rgba(52, 152, 219, 1)',
        borderWidth: 1,
      },
      {
        label: 'Planned ($)',
        data: plannedValues,
        backgroundColor: 'rgba(46, 204, 113, 0.6)',
        borderColor: 'rgba(46, 204, 113, 1)',
        borderWidth: 1,
      },
    ],
  };

  const options = {
    responsive: true,
    plugins: {
      legend: { position: 'top' },
      title: { display: true, text: 'Current vs Planned Expenditure by Category' },
    },
    scales: {
      y: {
        beginAtZero: true,
        title: { display: true, text: 'Amount ($)' },
      },
    },
  };

  return (
    <div className="chart-container">
      <Bar ref={ref} data={data} options={options} />
    </div>
  );
});

export default ExpenditureComparisonChart;
