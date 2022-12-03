function validate()
{
var username=document.getElementById("username").Value;
var password=document.getElementById("password").Value;
if(username == "admin" && password == "user")
{
    alert("Login is Succesvol");
    return false;
}
else
{
    alert("fout wachtwoord of gebruikersnaam");
}
}