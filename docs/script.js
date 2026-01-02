document.addEventListener('DOMContentLoaded', () => {
    fetch('data.json')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            renderData(data);
        })
        .catch(error => {
            console.error('Error loading data:', error);
            document.getElementById('connections-list').innerHTML =
                '<div class="no-data">❌ Could not load ferry data.</div>';
        });
});

function renderData(data) {
    const list = document.getElementById('connections-list');
    const updatedEl = document.getElementById('last-updated');

    if (data.updated_at) {
        updatedEl.textContent = `Last updated: ${data.updated_at}`;
    }

    if (!data.connections || data.connections.length === 0) {
        list.innerHTML = '<div class="no-data">No connections available at the moment.</div>';
        return;
    }

    list.innerHTML = '';
    data.connections.forEach(conn => {
        const card = document.createElement('div');
        card.className = 'connection-card';
        card.innerHTML = `
            <div class="connection-info">
                <div class="time">📅 ${conn.date} ⏰ ${conn.departure_time} - ${conn.arrival_time}</div>
                <div class="route">${conn.departure_harbor} ➡️ ${conn.arrival_harbor}</div>
            </div>
            <a href="${conn.booking_url}" target="_blank" class="btn">Book Now</a>
        `;
        list.appendChild(card);
    });
}
