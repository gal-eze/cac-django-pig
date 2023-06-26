  function updateData(data) {
      stockdata = data["StockData"];
      currentValue = parseFloat(data["CurrentValue"]).toFixed(2);
      unrealizedPNL = parseFloat(data["UnrealizedPNL"]).toFixed(2);
      growth = parseFloat(data["Growth"]).toFixed(2);
      var tableRows = document.getElementById("portfolio-table").tBodies[0].rows;
      for (var i = 0; i < tableRows.length; i++) {
          var tableData = tableRows[i].getElementsByTagName('td');
          tableData[3].innerHTML = "$ " + stockdata[tableRows[i].id]["LastTradingPrice"].toFixed(2);
          if (stockdata[tableRows[i].id]["PNL"] > 0) {
              tableData[5].style.color = "#34c38f";
              tableData[6].style.color = "#34c38f";
              tableData[5].innerHTML = "+ $ " + stockdata[tableRows[i].id]["PNL"].toFixed(2);
              tableData[6].innerHTML = "+ " + stockdata[tableRows[i].id]["NetChange"].toFixed(2) + " %";
          } else {
              tableData[5].style.color = "#f46a6a";
              tableData[6].style.color = "#f46a6a";
              tableData[5].innerHTML = "- $ " + Math.abs(stockdata[tableRows[i].id]["PNL"].toFixed(2));
              tableData[6].innerHTML = "- " + Math.abs(stockdata[tableRows[i].id]["NetChange"].toFixed(2)) + " %";
          }
      }
      var currentValueHeading = document.getElementById("current-value").getElementsByTagName("span")[0];
      currentValueHeading.innerHTML = currentValue;
      var unrealizedPNLHeading = document.getElementById("unrealized-pnl");
      var growthHeading = document.getElementById("growth");
      
      if (unrealizedPNL > 0) {
          unrealizedPNLHeading.style.color = ":#34c38f";
          growthHeading.style.color = ":#34c38f";
          unrealizedPNLHeading.getElementsByTagName("span")[0].innerHTML = "+ $ " + Math.abs(unrealizedPNL);
          growthHeading.getElementsByTagName("span")[0].innerHTML = "+ " + Math.abs(growth);
      } else {
          unrealizedPNLHeading.style.color = "#f46a6a";
          growthHeading.style.color = "#f46a6a";
          unrealizedPNLHeading.getElementsByTagName("span")[0].innerHTML = "- $ " + Math.abs(unrealizedPNL);
          growthHeading.getElementsByTagName("span")[0].innerHTML = "- " + Math.abs(growth);
      }
  }

  function getUpdatedValues() {
      $.ajax({
          type: "GET",
          url: "/update-prices",
          dataType: "json",
          success: function(data) {
              if (data.hasOwnProperty('Error')) {
                  console.log('Error at backend\n' + "Message: " + data['Error']);
              } else {
                  updateData(data);
              }
          }
      });
  }



  function addStockHoldingResult(data) {
      if (data === "Success") {
          $('#myModal').modal('toggle');
          alert("Stock Holding successfully added to your portfolio");
          location.reload();
      } else {
          alert("Error adding the stock holding\n"); // + "Message: " + data);
      }
  }

  $("#add-holding-form").submit(function(e) {
      e.preventDefault(); // avoid to execute the actual submit of the form.
      var form = $(this);
      var url = form.attr('action');
      $.ajax({
          type: "POST",
          url: url,
          data: form.serialize(),
          success: function(data) { addStockHoldingResult(data) }
      });
  });




  function getPortfolioInsights() {
      $.ajax({
          type: "GET",
          url: "/get-portfolio-insights",
          dataType: "json",
          success: function(data) {
              if (data.hasOwnProperty('Error')) {
                  // alert('Error at backend\n' + "Message: " + data['Error']);
                  getPortfolioInsights();
              } else {
                  var betaElement = document.getElementById("portfolio-beta");
                  var betaElementTxt = document.getElementById("portfolio-beta-text");
                  betaElement.innerHTML = parseFloat(data["PortfolioBeta"]).toFixed(2);
                  betaElementTxt.innerHTML = `Your portfolio moves by a factor of ${ parseFloat(data["PortfolioBeta"]).toFixed(2) } in the direction of market swing`;
                  var peElement = document.getElementById("portfolio-pe");
                  peElement.innerHTML = parseFloat(data["PortfolioPE"]).toFixed(2);
              }
          }
      });
  }

  function openTab(evt, tabName) {
      // Declare all variables
      var i, tabcontent, tablinks;
      // Get all elements with class="tabcontent" and hide them
      tabcontent = document.getElementsByClassName("tabcontent");
      for (i = 0; i < tabcontent.length; i++) {
          tabcontent[i].style.display = "none";
      }
      // Get all elements with class="tablinks" and remove the class "active"
      tablinks = document.getElementsByClassName("nav-link");
      for (i = 0; i < tablinks.length; i++) {
          tablinks[i].className = tablinks[i].className.replace(" active", "");
      }
      // Show the current tab, and add an "active" class to the button that opened the tab
      document.getElementById(tabName).style.display = "block";
      evt.currentTarget.className += " active";

      if (tabName === "portfolio-insights") {
          getPortfolioInsights();
      }
  }


  function generateRandomColors(length) {
      var colors = [];
      for (let i = 0; i < length; i++) {
          var randomColor = Math.floor(Math.random()*16777215).toString(16);
          colors.push("#" + randomColor);
      }
      return colors;
  }

  var accounts = {
      'data': [100],
      'labels': ['equity']
  };


  
  var sectors = {
      'data': sectorsdata,
      'labels': sectorslabels
  };



  var stocks = {
      'data': stocksdata,
      'labels': stockslabels
  };
  var accountChartConfig = {
      type: 'doughnut',
      data: {
          datasets: [{
              data: accounts['data'],
              backgroundColor: generateRandomColors(accounts['data'].length),
          }],
          // These labels appear in the legend and in the tooltips when hovering different arcs
          labels: accounts['labels']
      },
      options: {
          responsive: true,
          legend: {
          position: 'right',
          },
          animation: {
          animateScale: true,
          animateRotate: true
          }
      }
  };
  var sectorChartConfig = {
      type: 'doughnut',
      data: {
          datasets: [{
              data: sectors['data'],
              backgroundColor: generateRandomColors(sectors['data'].length),
          }],
          // These labels appear in the legend and in the tooltips when hovering different arcs
          labels: sectors['labels']
      },
      options: {
          responsive: true,
          legend: {
          position: 'right',
          },
          animation: {
          animateScale: true,
          animateRotate: true
          }
      }
  };
  var stockChartConfig = {
      type: 'doughnut',
      data: {
          datasets: [{
              data: stocks['data'],
              backgroundColor: generateRandomColors(stocks['data'].length),
          }],
          // These labels appear in the legend and in the tooltips when hovering different arcs
          labels: stocks['labels']
      },
      options: {
          responsive: true,
          legend: {
          position: 'right',
          },
          animation: {
          animateScale: true,
          animateRotate: true
          }
      }
  };
  window.onload = function() {
  var ctx1 = document.getElementById('account-chart-container').getContext('2d');
  window.myDoughnut1 = new Chart(ctx1, accountChartConfig);
  var ctx2 = document.getElementById('sector-chart-container').getContext('2d');
  window.myDoughnut2 = new Chart(ctx2, sectorChartConfig);
  var ctx3 = document.getElementById('stock-chart-container').getContext('2d');
  window.myDoughnut3 = new Chart(ctx3, stockChartConfig);
  };

