function toggleMenu(event) {
    event.preventDefault();
    document.querySelector('.menu').classList.toggle('active');
    document.querySelector('.toggle-nav').classList.toggle('active');
}

function showLinkedInForm() {
    var form = document.getElementById('linkedin-form');
    if (form.style.display === 'none' || form.style.display === '') {
        form.style.display = 'block';
    } else {
        form.style.display = 'none';
    }
}

document.getElementById('linkedin-credentials-form').addEventListener('submit', function (e) {
    e.preventDefault();
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
            alert(data.message);
            document.getElementById('linkedin-form').style.display = 'none';
        })
        .catch((error) => {
            console.error('Error:', error);
            alert('An error occurred while processing your request.');
        });
});



