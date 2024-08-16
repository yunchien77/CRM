function toggleMenu(event) {
    event.preventDefault();
    document.querySelector('.menu').classList.toggle('active');
    document.querySelector('.toggle-nav').classList.toggle('active');
}

function toggleSocialSearch() {
    var menu = document.getElementById('social-search-menu');
    if (menu.style.display === 'none' || menu.style.display === '') {
        menu.style.display = 'block';
    } else {
        menu.style.display = 'none';
    }
}

function showLinkedinForm() {
    var form = document.getElementById('linkedin-form');
    if (form.style.display === 'none' || form.style.display === '') {
        form.style.display = 'block';
    } else {
        form.style.display = 'none';
    }
}

function showGoogleForm() {
    var form = document.getElementById('google-form');
    if (form.style.display === 'none' || form.style.display === '') {
        form.style.display = 'block';
    } else {
        form.style.display = 'none';
    }
}

function showCustomForm() {
    var form = document.getElementById('google-custom-form');
    if (form.style.display === 'none' || form.style.display === '') {
        form.style.display = 'block';
    } else {
        form.style.display = 'none';
    }
}

document.getElementById('linkedin-credentials-form').addEventListener('submit', function (e) {
    e.preventDefault();
    document.getElementById('linkedin-search-status').textContent = 'Searching...';

    var username = document.getElementById('linkedin-username').value;
    var password = document.getElementById('linkedin-password').value;

    // Send credentials to the server
    fetch('/run-linkedin-search', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username: username, password: password }),
    })
        .then(response => response.json())
        .then(data => {
            /*alert(data.message);*/
            document.getElementById('linkedin-search-status').textContent = data.message;
            /*document.getElementById('linkedin-form').style.display = 'none';*/
        })
        .catch((error) => {
            console.error('Error:', error);
            /*alert('An error occurred while processing your request.');*/
            document.getElementById('linkedin-search-status').textContent = 'An error occurred.';
        });
});

document.getElementById('google-search-form').addEventListener('submit', function (e) {
    e.preventDefault();

    // Show loading indicator
    document.getElementById('google-search-status').textContent = 'Searching...';

    // Send request to start Google search
    fetch('/run-google-search', {
        method: 'POST',
    })
        .then(response => response.json())
        .then(data => {
            document.getElementById('google-search-status').textContent = data.message;
        })
        .catch((error) => {
            console.error('Error:', error);
            document.getElementById('google-search-status').textContent = 'An error occurred.';
        });
});

document.getElementById('google-custom-search-form').addEventListener('submit', function (e) {
    e.preventDefault();

    // Show loading indicator
    document.getElementById('google-custom-search-status').textContent = 'Searching...';

    // Send request to start Google search
    fetch('/run-custom-search', {
        method: 'POST',
    })
        .then(response => response.json())
        .then(data => {
            document.getElementById('google-custom-search-status').textContent = data.message;
        })
        .catch((error) => {
            console.error('Error:', error);
            document.getElementById('google-custom-search-status').textContent = 'An error occurred.';
        });
});
