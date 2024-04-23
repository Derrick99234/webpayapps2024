document.addEventListener("DOMContentLoaded", function () {
  let loginButton = document.querySelector(".btn2");
  let registerButton = document.querySelector(".btn23");

  function changeRoute() {
    // alert("done bruh");
    window.location.href = "/login";
  }

  loginButton.addEventListener("click", function () {
    setTimeout(changeRoute, 1000);
  });

  registerButton.addEventListener("click", function () {
    window.location.href = "/register";
  });
});
