📝 Flask Blog Website

A multi-user blog website built with Flask, SQLAlchemy, and Bootstrap 5. It features user authentication, admin-only post management, comments, Gravatar avatars, and a contact form powered by Gmail SMTP.

🚀 Features

✅ User registration and login ✅ Admin-only post creation, editing, and deletion ✅ Rich-text posts using Flask-CKEditor ✅ Commenting system on posts ✅ Gravatar integration for user avatars ✅ Bootstrap 5 for responsive design ✅ Secure password hashing with Werkzeug ✅ Contact form with Gmail SMTP ✅ Modular Flask-WTF forms

🛠️ Technologies Used

Python Flask Flask-Bootstrap Flask-CKEditor Flask-Gravatar Flask-Login Flask-WTF / WTForms Flask-SQLAlchemy / SQLAlchemy python-dotenv SMTP (Gmail)

⚙️ Installation & Setup 1️⃣ Clone the Repository git clone https://github.com/saksham-s18/My-Blogs-Website.git cd My-Blogs-Website

2️⃣ Create Virtual Environment & Install Dependencies python3 -m venv venv source venv/bin/activate # On Windows use: venv\Scripts\activate pip install -r requirements.txt

requirements.txt should include:

Flask Flask-Bootstrap Flask-CKEditor Flask-Gravatar Flask-Login Flask-WTF WTForms Flask-SQLAlchemy python-dotenv

3️⃣ Configure Environment Variables

Create a .env file in the project root:

FLASK_KEY=your_flask_secret_key DB_URI=sqlite:///posts.db EMAIL_KEY=your_gmail_address PASSWORD_KEY=your_gmail_app_password

⚠️ Use a Gmail App Password if your account has 2FA enabled.

4️⃣ Database Setup

The app automatically creates posts.db and all tables when run for the first time.

5️⃣ Run the App python main.py

The app runs at http://localhost:5002 (you can change the port in main.py).

💡 Usage

🧍‍♂️ Register: Visit /register to create a user.

🔐 Login: Visit /login to sign in.

🧑‍💼 Admin user (ID = 1) can create, edit, and delete posts.

💬 Logged-in users can comment on posts.

✉️ Contact form available at /contact.

ℹ️ Learn more on the /about page.

📁 Project Structure flask-blog/ ├── main.py ├── forms.py ├── templates/ │ ├── base.html │ ├── index.html │ ├── register.html │ ├── login.html │ ├── make-post.html │ ├── post.html │ ├── about.html │ ├── contact.html ├── static/ │ └── (your css/js/images) ├── .env ├── requirements.txt └── README.md

🧩 Template Notes

All templates inherit from base.html.

Posts are shown on index.html.

Individual posts use post.html.

Forms are built with Flask-WTF.

🎨 Customization

🔧 Change email settings in .env for the contact form. 🎨 Edit templates in /templates to redesign pages. 🗃️ Modify models in main.py for new features. 💅 Add custom CSS/JS in /static.

❓ Frequently Asked Questions

Q: Who is the admin? A: The user with id == 1 is the default admin.

Q: How are passwords stored? A: Passwords are securely hashed using Werkzeug (PBKDF2).

Q: Can I add more admins? A: Yes — modify the admin_only decorator to support multiple admin IDs.

🤝 Contributing

Contributions are welcome!

Fork the repository

Create a new branch

Commit your changes

Submit a pull request 🚀

📜 License

Licensed under the MIT License — free to use and modify.

📬 Contact

For issues or inquiries, use the contact form on the website or email the project maintainer directly.