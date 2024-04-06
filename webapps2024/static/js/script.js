document.addEventListener("DOMContentLoaded", function () {
  let loginButton = document.querySelector(".btn3");
  function changeRoute() {
    alert("done bruh");
    window.location.href = "/login";
  }

  loginButton.addEventListener("click", function () {
    setTimeout(changeRoute, 1000);
  });
});
