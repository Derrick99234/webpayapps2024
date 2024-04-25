let loginButton = document.querySelector(".btn2");
let registerButton = document.querySelector(".btn23");

function changeRoute() {
  // alert("done bruh");
  window.location.href = "/login";
}

if (registerButton) {
  registerButton.addEventListener("click", function () {
    window.location.href = "/register";
  });
}

if (loginButton) {
  loginButton.addEventListener("click", function () {
    setTimeout(changeRoute, 1000);
  });
}

console.log(registerButton);
console.log("registerButton");
