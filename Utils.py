# URL = "https://salesweb.civilview.com/Sales/SalesSearch?countyId=25"
# print("Enter URL:")
# URL = input()
URL = "https://salesweb.civilview.com/"


headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
}

columns_needed = [
    "Sheriff #",
    "Sales Date",
    "Address"
]

# HTML template with two buttons
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Scraper Control Panel</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #f4f7f8;
            color: #333;
            margin: 0;
            padding: 0;
        }
        .container {
            width: 80%;
            margin: 50px auto;
            background: #fff;
            padding: 30px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            border-radius: 8px;
        }
        h1 {
            text-align: center;
            color: #4CAF50;
        }
        .button {
            background: #4CAF50;
            color: #fff;
            border: none;
            padding: 15px 30px;
            margin: 10px;
            font-size: 16px;
            border-radius: 5px;
            cursor: pointer;
            transition: background 0.3s ease;
        }
        .button:hover {
            background: #45a049;
        }
        #progressContainer {
            width: 100%;
            background: #ddd;
            border-radius: 5px;
            overflow: hidden;
            margin-top: 20px;
        }
        #progressBar {
            height: 30px;
            width: 0%;
            background: #4CAF50;
            text-align: center;
            line-height: 30px;
            color: white;
        }
        /* Toast Notification Styles */
        #notification {
            position: fixed;
            top: 20px;
            right: 20px;
            background-color: #4CAF50;
            color: #fff;
            padding: 15px;
            border-radius: 5px;
            opacity: 0;
            transition: opacity 0.5s ease-in-out;
            z-index: 1000;
            min-width: 200px;
            text-align: center;
        }
        #notification.show {
            opacity: 1;
        }
        #notification.error {
            background-color: #f44336;
        }
    </style>
    <script>
        // Display toast notification.
        function showNotification(message, type) {
            var notification = document.getElementById('notification');
            notification.textContent = message;
            notification.className = 'show';
            if(type === 'error'){
                notification.classList.add('error');
            }
            // Hide notification after 3 seconds.
            setTimeout(function(){
                notification.className = notification.className.replace('show', '');
            }, 3000);
        }

        function runScraper() {
            // Reset progress bar.
            document.getElementById('progressBar').style.width = '0%';
            document.getElementById('progressBar').textContent = '0%';
            fetch("/run-scraper")
            .then(response => response.json())
            .then(data => {
                showNotification(data.message, 'success');
            })
            .catch(error => {
                showNotification("Error running scraper: " + error, 'error');
            });
        }

        function pollProgress() {
            fetch("/progress")
            .then(response => response.json())
            .then(data => {
                let progressBar = document.getElementById('progressBar');
                progressBar.style.width = data.progress + '%';
                progressBar.textContent = data.progress + '%';
            })
            .catch(error => {
                console.error("Error fetching progress: ", error);
            });
        }
        // Poll progress every 500ms.
        setInterval(pollProgress, 500);
    </script>
</head>
<body>
    <div class="container">
        <h1>Scraper Control Panel</h1>
        <div style="text-align: center;">
            <button class="button" onclick="runScraper()">Run Scraper</button>
            <a href="/download-excel"><button class="button">Download Excel</button></a>
        </div>
        <div id="progressContainer">
            <div id="progressBar">0%</div>
        </div>
    </div>
    <!-- Toast notification element -->
    <div id="notification"></div>
</body>
</html>
'''
