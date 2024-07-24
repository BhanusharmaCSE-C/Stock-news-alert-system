document.getElementById('stock-form').addEventListener('submit', function (e) {
    e.preventDefault();
    const stockSymbol = document.getElementById('stock-symbol').value;
    getStockData(stockSymbol);
});

async function getStockData(stockSymbol) {
    const response = await fetch(`/stock?stock=${stockSymbol}`);
    const data = await response.json();

    if (data.error) {
        document.getElementById('result').innerHTML = 'Error fetching stock data. Please check the stock symbol.';
        return;
    }

    const { stock, up_down, diff_percent, articles } = data;
    let resultHTML = `<h2>${stock}: ${up_down}${diff_percent}%</h2>`;

    if (articles.length > 0) {
        articles.forEach(article => {
            resultHTML += `<h3>${article.title}</h3><p>${article.description}</p><a href="${article.url}" target="_blank">Read more</a><hr>`;
        });
    } else {
        resultHTML += `<p>No significant changes.</p>`;
    }

    document.getElementById('result').innerHTML = resultHTML;
}
