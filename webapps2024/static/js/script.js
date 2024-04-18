document.addEventListener("DOMContentLoaded", function () {
  let loginButton = document.querySelector(".btn2");

  function changeRoute() {
    alert("done bruh");
    window.location.href = "/register";
  }

  loginButton.addEventListener("click", function () {
    setTimeout(changeRoute, 1000);
  });
});
