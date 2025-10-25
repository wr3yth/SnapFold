# ⚡ SnapFold  
### Compact your entire project into one beautiful Markdown file.

Built for developers who want to **share, archive, or feed full projects into AI** — without any mess.

## What is SnapFold?

**SnapFold** is a Python utility that crawls your entire project folder and folds it into **one clean, structured `.md` file**.  
It preserves folder hierarchy, includes file contents inline, and makes everything beautifully readable — perfect for:

- 🧩 AI model input (LLMs like ChatGPT, Claude, etc.)
- 💾 Compact code archiving
- 🧠 Quick sharing and review
- 🧰 Offline project documentation

## how to use:

🧩 Step 1: Place snapfold.py in your project folder
        you can do it manually or use this command:
        ```clone https://github.com/wr3yth/SnapFold.git ```
        then drag out the snapfold.py into your target folder.
🚀 Step 2: Run SnapFold!
           
           ```python snapfold.py```
           

💯 Step 2:that's it! 
       just for the first time you run it, it'll ask you 
    


## How would the result look like?

 the result file will look like this:
    ```
    / (project root)
├── index.html 
├── style.css
├── script.js
└── /wiki/
    ├── effects.html
    └── interactions.json
    
---

### 📄 index.html
```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <title>My Cool Website</title>
  </head>
  <body>
    <h1>Hello, world!</h1>
  </body>
</html>
```

---

### 🎨 style.css
```css
body {
  font-family: sans-serif;
  background: #111;
  color: #f5f5f5;
}
```

---

### ⚙️ script.js


    ```
