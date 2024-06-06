import React, { useState, useEffect } from "react";
import axios from "axios";
import { Charts } from "./components/Charts"; // Chart bileşenini içe aktarıyoruz
import "./App.css";

function App() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    axios
      .get("http://127.0.0.1:5000/data")
      .then((response) => {
        setData(response.data);
        setLoading(false);
      })
      .catch((error) => {
        setError(error);
        setLoading(false);
      });
  }, []); // Boş bağımlılık dizisi ile sadece bileşen ilk yüklendiğinde çalışır

  if (loading) {
    return <div>Yükleniyor...</div>;
  }

  if (error) {
    return <div>Hata: {error.message}</div>;
  }

  const allMachineData = data;
  const labels = Object.keys(allMachineData).filter((label) => !label.includes("StartDate"));

  const labelColors = (label) => {
    if (label.startsWith("M8")) {
      return "rgba(255, 99, 132, 0.6)"; // Kırmızı
    } else if (label.startsWith("M16")) {
      return "rgba(94, 62, 235, 0.6)"; // Mavi
    } else if (label.startsWith("M12")) {
      return "rgba(75, 192, 192, 0.6)"; // Yeşil
    } else if (label.startsWith("M24")) {
      return "rgba(153, 102, 255, 0.6)"; // Mor
    } else if (label.startsWith("M18")) {
      return "rgba(255, 159, 64, 0.6)"; // Turuncu
    } else if (label.startsWith("M20")) {
      return "rgba(255, 205, 86, 0.6)"; // Sarı
    } else if (label.startsWith("M27")) {
      return "rgba(54, 162, 235, 0.1)"; // Mavi
    } else if (label.startsWith("SP")) {
      return "rgba(153, 102, 255, 0.6)"; // Mor
    } else {
      return "rgba(201, 203, 207, 0.6)"; // Gri
    }
  };

  const datasets = labels.map((label) => {
    const machineData = allMachineData[label];
    return {
      label: `${machineData[0][0].substring(0, 10)}`,
      machineData: machineData, // Machine data arrayını etiketle birlikte sakla
      data: machineData.map((item) => item[1]), // Süreleri al
      backgroundColor: machineData.map((item) => labelColors(item[0])),
      borderColor: machineData.map((item) => labelColors(item[0])),
      borderWidth: 1,
      key: label // Her veri kümesi için benzersiz bir anahtar
    };
  });

  const chartData = {
    labels: labels,
    datasets: datasets,
  };

  const options = {
    scales: {
      y: {
        beginAtZero: true,
        stacked: true, // Çubukların üst üste yığılmasını sağlar
      },
      x: {
        stacked: true, // Çubukların üst üste yığılmasını sağlar
      },
    },
    plugins: {
      tooltip: {
        callbacks: {
          label: function (tooltipItem) {
            const dataset = tooltipItem.dataset;
            const index = tooltipItem.dataIndex;
            const machineData = dataset.machineData[index];
            const time = Number(machineData[1]).toFixed(3);
            return `${machineData[0]}: ${time}`;
          },
        },
      },
    },
  };

  return (
    <div>
      <h1>Çalışma Süreleri</h1>
      <Charts chartData={chartData} options={options} />
    </div>
  );
}

export default App;
