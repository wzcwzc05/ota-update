document
  .getElementById("login-form")
  .addEventListener("submit", function (event) {
    event.preventDefault();

    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;
    url = "/login?username=" + username + "&password=" + password;
    fetch(url)
      .then((response) => response.json())
      .then((data) => {
        console.log(data);
        const responseElement = document.getElementById("response");
        if (data.status === "success") {
          responseElement.textContent = data.message;
          responseElement.style.color = "green";
          window.location.href = "/dashboard"; // 登录成功后跳转到仪表盘页面
        } else {
          responseElement.textContent = data.message;
          responseElement.style.color = "red";
        }
      });
  });
