document.addEventListener('DOMContentLoaded', function() {
    const tableBody = document.querySelector('#stockTable tbody');
    const averageValueSumCell = document.getElementById('averageValueSum');
    const currentValueSumCell = document.getElementById('currentValueSum');

    function fetchAndDisplayData() {
        fetch('/api/stocks')
            .then(response => response.json())
            .then(data => {
                tableBody.innerHTML = '';  // Clear the table
                let averageValueSum = 0;
                let currentValueSum = 0;

                data.forEach(stock => {
                    // Calculate total values for summary
                    averageValueSum += stock.average_value;
                    currentValueSum += stock.current_value;

                    // Determine color and arrow for Last Price
                    let lastPriceColor = 'black';
                    let lastPriceArrow = '■';
                    if (stock.last_price > stock.prev_last_price) {
                        lastPriceColor = 'green';
                        lastPriceArrow = '▲';
                    } else if (stock.last_price < stock.prev_last_price) {
                        lastPriceColor = 'red';
                        lastPriceArrow = '▼';
                    }

                    // Determine color and arrow for Day High (comparison with previous Day High)
                    let dayHighColor = 'black';
                    let dayHighArrow = '■';
                    if (stock.day_high > stock.prev_day_high) {
                        dayHighColor = 'green';
                        dayHighArrow = '▲';
                    } else if (stock.day_high < stock.prev_day_high) {
                        dayHighColor = 'red';
                        dayHighArrow = '▼';
                    }

                    // Determine color and arrow for Day Low (comparison with previous Day Low)
                    let dayLowColor = 'black';
                    let dayLowArrow = '■';
                    if (stock.day_low > stock.prev_day_low) {
                        dayLowColor = 'red';
                        dayLowArrow = '▼';  // Lower price is worse for Low
                    } else if (stock.day_low < stock.prev_day_low) {
                        dayLowColor = 'green';
                        dayLowArrow = '▲';  // Higher price is better for Low
                    }

                    // Add stock row to the table
                    const row = `
                        <tr>
                            <td>${stock.serial_number}</td>
                            <td title="${stock.company_name}">${stock.symbol}</td>
                            <td>${stock.qoh}</td>
                            <td>${stock.average_price.toFixed(2)}</td>
                            <td style="color: ${lastPriceColor};">${stock.last_price.toFixed(2)} ${lastPriceArrow}</td>
                            <td>${stock.last_updated}</td>
                            <td>${stock.change.toFixed(2)}</td>
                            <td>${stock.percentage_change.toFixed(2)}%</td>
                            <td>${stock.previous_close.toFixed(2)}</td>
                            <td>${stock.open_price.toFixed(2)}</td>
                            <td style="color: ${dayHighColor};">${stock.day_high.toFixed(2)} ${dayHighArrow}</td>
                            <td style="color: ${dayLowColor};">${stock.day_low.toFixed(2)} ${dayLowArrow}</td>
                            <td>${stock.week_high.toFixed(2)}</td>
                            <td>${stock.week_low.toFixed(2)}</td>
                            <td>${stock.average_value.toFixed(2)}</td>
                            <td>${stock.current_value.toFixed(2)}</td>
                        </tr>
                    `;
                    tableBody.insertAdjacentHTML('beforeend', row);
                });

                // Update summary values
                averageValueSumCell.textContent = averageValueSum.toFixed(2);
                currentValueSumCell.textContent = currentValueSum.toFixed(2);
            })
            .catch(error => console.error('Error fetching stock data:', error));
    }

    // Fetch and display data on page load
    fetchAndDisplayData();

    // Set an interval to refresh the data every 15 seconds
    setInterval(fetchAndDisplayData, 15 * 1000);
});
