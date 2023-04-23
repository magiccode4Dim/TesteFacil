
function meuRelogio() {
            setInterval (function() {
                var hora = new Date().toLocaleTimeString();
                document.getElementById('rel').innerHTML = hora;
              }, 1000);
}    