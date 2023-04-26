
const url1 =  '/user/perguntasqunt';
const cookie2 = document.cookie;

fetch(url1, {
  headers: {
    'Cookie': cookie2
  }
})
  .then(response => response.json())
  .then(data => {
		console.log(data)
		// chart 6
		Highcharts.chart('chart6', {
			chart: {
				type: 'pie',
				options3d: {
					enabled: true,
					alpha: 45
				}
			},
			title: {
				text: 'Este Gráfico contém a quantidade de perguntas que o Estudante Acertou, errou e não respondeu'
			},
			plotOptions: {
				pie: {
					innerSize: 100,
					depth: 45
				}
			},
			series: [{
				name: 'Quantidade de Perguntas',
				data: [
				['Erradas', data.Erradas],
				['Não Respondidas', data.NRespondidas],
				['Certas', data.Certas]
				]
			}]
		});




			
  })
  .catch(error => console.error(error));






