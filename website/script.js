document.getElementById('fileInput').addEventListener('change', function (e) {
    const file = e.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = function (event) {
        const csvData = event.target.result;
        const rows = csvData.split('\n').slice(1);  // Skip header row

        const speedingData = [];
        const swervingData = [];
        const labels = [];

        rows.forEach(row => {
            const [date, speeding, swerving] = row.split(',').map((item) => item.trim());
            if (date && speeding && swerving) {
                labels.push(date);
                speedingData.push(Number(speeding));
                swervingData.push(Number(swerving));
            }
        });

        displayCharts(labels, speedingData, swervingData);
    };
    reader.readAsText(file);
});

function displayCharts(labels, speedingData, swervingData) {
    document.querySelector('.chart-container').style.display = 'flex';

    const ctx = document.getElementById('combinedChart').getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Speeding Incidents',
                    data: speedingData,
                    borderColor: 'rgba(255, 99, 132, 1)',
                    fill: false,
                },
                {
                    label: 'Swerving Incidents',
                    data: swervingData,
                    borderColor: 'rgba(54, 162, 235, 1)',
                    fill: false,
                }
            ]
        },
        options: {
            scales: {
                y: {
                    min: 0,
                    max: Math.max(30, Math.max(...speedingData), Math.max(...swervingData)),
                    beginAtZero: true
                }
            },
            legend: {
                onClick: function(event, legendItem) {
                    const index = legendItem.datasetIndex;
                    const meta = this.getDatasetMeta(index);

                    // Toggle the visibility
                    meta.hidden = meta.hidden === null ? !this.data.datasets[index].hidden : null;
                    this.update();
                }
            }
        }
    });
}
