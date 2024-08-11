<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <title>File Upload</title>
    <style>
        body {
            font-family: Arial, sans-serif;
        }

        .container {
            max-width: 500px;
            margin: auto;
            padding: 20px;
            border: 1px solid #ccc;
            border-radius: 5px;
        }

        .error {
            color: red;
        }

        .success {
            color: green;
        }
    </style>
</head>

<body>
    <div class="container">
        <h2>Upload a File (Minimum 10 MB)</h2>
        <?php
        if ($_SERVER['REQUEST_METHOD'] == 'POST') {
            $target_dir = "uploads/";
            $target_file = $target_dir . basename($_FILES["fileToUpload"]["name"]);
            $uploadOk = 1;
            $fileSize = $_FILES["fileToUpload"]["size"];
            $fileType = strtolower(pathinfo($target_file, PATHINFO_EXTENSION));

            if ($fileSize < 10485760) {
                echo "<p class='error'>File must be at least 10 MB.</p>";
                $uploadOk = 0;
            }
            if ($fileSize > 524288000) {
                echo "<p class='error'>File must be less than 500 MB.</p>";
                $uploadOk = 0;
            }
            if ($uploadOk == 0) {
                echo "<p class='error'>Sorry, your file was not uploaded.</p>";
            } else {
                if (move_uploaded_file($_FILES["fileToUpload"]["tmp_name"], $target_file)) {
                    echo "<p class='success'>The file " . htmlspecialchars(basename($_FILES["fileToUpload"]["name"])) . " has been uploaded.</p>";
                } else {
                    echo "<p class='error'>Sorry, there was an error uploading your file.</p>";
                }
            }
        }
        ?>
        <form action="index.php" method="post" enctype="multipart/form-data">
            Select file to upload:
            <input type="file" name="fileToUpload" id="fileToUpload" required>
            <br><br>
            <input type="submit" value="Upload File" name="submit">
        </form>
    </div>
</body>

</html>