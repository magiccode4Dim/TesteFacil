
const url =  '/user/getnotasedadastese';
const cookie = document.cookie;

fetch(url, {
  headers: {
    'Cookie': cookie
  }
})
  .then(response => response.json())
  .then(data => {
		console.log(data)
			var options = {
				series: [{
					name: 'Nota',
					data: data.notas
				}],
				chart: {
					height: 350,
					type: 'line',
					toolbar: {
						show: false,
					}
				},
				grid: {
					show: false,
					padding: {
						left: 0,
						right: 0
					}
				},
				stroke: {
					width: 7,
					curve: 'smooth'
				},
				xaxis: {
					//type: 'datetime',
					//categories: data.datas
					categories: ['Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct','Nov','Dec']
				},
				title: {
					text: 'Notas do Estudante',
					align: 'left',
					style: {
						fontSize: "16px",
						color: '#666'
					}
				},
				fill: {
					type: 'gradient',
					gradient: {
						shade: 'dark',
						gradientToColors: [ '#1b00ff'],
						shadeIntensity: 1,
						type: 'horizontal',
						opacityFrom: 1,
						opacityTo: 1,
						stops: [0, 100, 100, 100]
					},
				},
				markers: {
					size: 4,
					colors: ["#FFA41B"],
					strokeColors: "#fff",
					strokeWidth: 2,
					hover: {
						size: 7,
					}
				},
				yaxis: {
					min: 0,
					max: 30,
					title: {
						text: 'Notas',
					},
				}
			};
			var chart = new ApexCharts(document.querySelector("#chart1"), options);
			chart.render();
  })
  .catch(error => console.error(error));



 //para docente 
const url2 =  '/teacher/getcenr';
const cookie2 = document.cookie;

fetch(url2, {
  headers: {
    'Cookie': cookie2
  }
})
  .then(response => response.json())
  .then(data => {
		console.log(data)
		
		var options4 = {
			series: [{
				name:'Erradas',
				data: data.erradas
			}, {
				name:'Certas',
				data: data.certas
			},{
				name: 'Não Respondidas',
				data: data.nrespond
			}],
			chart: {
				type: 'bar',
				height: 430,
				toolbar: {
					show: false,
				}
			},
			grid: {
				show: false,
				padding: {
					left: 0,
					right: 0
				}
			},
			plotOptions: {
				bar: {
					horizontal: true,
					dataLabels: {
						position: 'top',
					},
				}
			},
			dataLabels: {
				enabled: true,
				offsetX: -6,
				style: {
					fontSize: '12px',
					colors: ['#fff']
				}
			},
			stroke: {
				show: true,
				width: 1,
				colors: ['#fff']
			},
			xaxis: {
				categories: data.testes,
			},
		};
		var chart = new ApexCharts(document.querySelector("#chart4"), options4);
		chart.render();
		
			
  })
  .catch(error => console.error(error));


