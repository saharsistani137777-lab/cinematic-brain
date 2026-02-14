function updateBrainActivity(activity) {
    const regions = {
        'prefrontal': 'brain-prefrontal',
        'limbic': 'brain-limbic',
        'visual': 'brain-visual'
    };
    
    for (let [region, elementId] of Object.entries(regions)) {
        if (activity[region] !== undefined) {
            const percent = Math.round(activity[region] * 100);
            document.getElementById(elementId).style.width = percent + '%';
            document.getElementById(elementId).textContent = region + ' ' + percent + '%';
        }
    }
}

function loadRecommendationsForMovie(movieId) {
    fetch(/api/recommend/${currentUserId}?movie_id=${movieId}&n=6)
        .then(response => response.json())
        .then(data => {
            if (data.recommendations) {
                const container = document.getElementById('recommendations-container');
                container.innerHTML = '<h6 class="col-12 text-white-50 mb-3">Neural Recommendations:</h6>';
                
                data.recommendations.forEach(movie => {
                    const col = document.createElement('div');
                    col.className = 'col-md-6 col-lg-4';
                    col.innerHTML = 
                        <div class="movie-card" onclick="analyzeBrain(${movie.id})">
                            <div class="movie-title">${movie.title}</div>
                            <div class="movie-rating">⭐ <span>${movie.rating.toFixed(1)}/10</span></div>
                        </div>
                    ;
                    container.appendChild(col);
                });
            }
        });
}

function loadBrainRecommendations(waveType) {
    fetch(/api/brain/recommend/${currentUserId}?wave=${waveType}&n=6)
        .then(response => response.json())
        .then(data => {
            if (data.recommendations) {
                const container = document.getElementById('recommendations-container');
                container.innerHTML = <h6 class="col-12 text-white-50 mb-3">${data.wave.toUpperCase()} Wave Recommendations:</h6>;
                
                data.recommendations.forEach(movie => {
                    const col = document.createElement('div');
                    col.className = 'col-md-6 col-lg-4';
                    col.innerHTML = 
                        <div class="movie-card" onclick="analyzeBrain(${movie.id})">
                            <div class="movie-title">${movie.title}</div>
                            <div class="movie-rating">⭐ <span>${movie.rating.toFixed(1)}/10</span></div>
                        </div>
                    ;
                    container.appendChild(col);
                });
            }
        });
}

function loadRandomMovie() {
    fetch('/api/movies/popular?limit=50')
        .then(response => response.json())
        .then(data => {
            if (data.movies && data.movies.length > 0) {
                const randomIndex = Math.floor(Math.random() * data.movies.length);
                analyzeBrain(data.movies[randomIndex].id);
            }
        });
}

function showNotification(message, type) {
    const toast = document.createElement('div');
    toast.className = position-fixed top-0 end-0 m-3 alert alert-${type === 'success' ? 'success' : 'danger'} alert-dismissible fade show;
    toast.style.zIndex = '9999';
    toast.innerHTML = 
        ${message}
        <button type="button" class="btn-close" onclick="this.parentElement.remove()"></button>
    ;
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.remove();
    }, 3000);
}
