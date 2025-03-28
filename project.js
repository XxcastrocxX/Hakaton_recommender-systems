document.getElementById('search-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const query = document.getElementById('search-input').value.trim();
    if (!query) return;

    const resultsContainer = document.getElementById('results-container');
    resultsContainer.innerHTML = '<p style="text-align: center; font-size: 24px;">Ищем...</p>';

    try {
        // Пример: заглушка для теста (замените на реальный API)
        const mockData = [
            { name: "Starbucks", type: "Кофейня", rating: "4.5", competitors: ["Blue Bottle", "Кофемания"] },
            { name: "Blue Bottle", type: "Кофейня", rating: "4.7", competitors: ["Starbucks", "Циферблат"] }
        ];
        
        // Фильтрация "как будто" по API
        const filteredData = mockData.filter(item => 
            item.name.toLowerCase().includes(query.toLowerCase())
        );

        displayResults(filteredData);
    } catch (error) {
        resultsContainer.innerHTML = '<p style="color: red; text-align: center;">Ошибка при поиске</p>';
    }
});

function displayResults(data) {
    const resultsContainer = document.getElementById('results-container');
    
    if (data.length === 0) {
        resultsContainer.innerHTML = '<p style="text-align: center; font-size: 50px;">Ничего не найдено</p>';
        return;
    }

    let html = '';
    data.forEach(item => {
        html += `
            <div style="margin: 20px auto; padding: 20px; background: white; border-radius: 8px; max-width: 700px;">
                <h2 style="color: #2946FF; margin: 0;">${item.name}</h2>
                <p><strong>Тип:</strong> ${item.type}</p>
                <p><strong>Рейтинг:</strong> ${item.rating}</p>
                <p><strong>Конкуренты:</strong> ${item.competitors.join(', ')}</p>
            </div>
        `;
    });

    resultsContainer.innerHTML = html;
}