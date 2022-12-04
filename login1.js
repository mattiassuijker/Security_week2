function validate()
{
var username=document.getElementById("username").Value;
var password=document.getElementById("password").Value;
if(username == "admin" && password == "user")
{
    window.location.assign("home.html");
    alert("Login is Succesvol");
}
else
{
    alert("fout wachtwoord of gebruikersnaam");
    return;
}
}