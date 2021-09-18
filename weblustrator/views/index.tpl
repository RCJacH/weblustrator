<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Weblustrator</title>
  <link rel="stylesheet" href="https://unpkg.com/mvp.css">
</head>
<body>
  <main>
    <h1>List of Pages</h1>
    % for post in posts:
    <ul>
        <li>
          <button onclick="render_page('{{ post.path }}')">Render</button>
          <a href="{{ post.path }}">{{ post.path }}</a>
        </li>
    </ul>
    % end
  </main>
  <script>
  function render_page(path) {
      var xhr = new XMLHttpRequest();
      xhr.open("POST", '/render/' + path);
      xhr.send()
  }
  </script>
</body>
</html>
