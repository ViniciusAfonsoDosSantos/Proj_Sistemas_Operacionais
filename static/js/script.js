let numeroProcessos = 0;

document.addEventListener('DOMContentLoaded', function () {
  const tempoChegadaInput = document.getElementById('tempoChegadaInput');
  const tempoServicoInput = document.getElementById('tempoServicoInput');
  const prioridadeInput = document.getElementById('prioridadeInput');
  const adicionarProcessoButton = document.getElementById('addProcessButton');
  const divProcessos = document.getElementById('divProcessos');
  const processTableRows = document.getElementById('processTableRows');
  const gerenciadorProcessos = document.getElementById('processButton');
  const divOpcoesProcesso = document.getElementById('div_opcoes_gerenciador_processos');
  const tipoProcessoSelecionado = document.getElementById('algorithmSelect');

  adicionarProcessoButton.addEventListener('click', function () {

    //Validação campos vazios
    if (tempoChegadaInput.value === '' || tempoServicoInput.value === '' || prioridadeInput.value === '') {
      //Adicionar classe(is-invalid) nos inputs
      return;
    }

    //Validação numero maximo de processos
    if (numeroProcessos >= 10) {
      alert('Número máximo de processos atingido');
      return;
    }

    numeroProcessos++;
    //Adiciona o processo na tabela
    const html = `
              <tr>
                <td>P${numeroProcessos}</td>
                <td>${tempoChegadaInput.value} </td>
                <td>${tempoServicoInput.value}</td>
                <td>${prioridadeInput.value}</td>
              </tr>
        `;
    processTableRows.innerHTML += html;
    divProcessos.hidden = false;

    //Ao atingir 5 processos, o botão de gerenciamento de processos e o select de tipo de processo é habilitado
    if (numeroProcessos >= 5) {
      divOpcoesProcesso.hidden = false;
    }

  });

  //recebe os dados dos processos e envia para o servidor
  gerenciadorProcessos.addEventListener('click', function () {
    let tabelaProcessos = document.getElementById('processTableRows');
    let dadosProcessos = [];
    let opcaoSelecionada = tipoProcessoSelecionado.options[tipoProcessoSelecionado.selectedIndex].value;

    for (let i = 0; i < tabelaProcessos.rows.length; i++) {
      let processo = {
        nome: tabelaProcessos.rows[i].cells[0].innerText,
        tempoChegada: tabelaProcessos.rows[i].cells[1].innerText,
        tempoServico: tabelaProcessos.rows[i].cells[2].innerText,
        prioridade: tabelaProcessos.rows[i].cells[3].innerText
      };
      dadosProcessos.push(processo);
    }

    //Manda o objeto como JSON para o servidor
    $.ajax({
      url: '/gerenciador-processos',
      type: 'GET',
      data: {
        processos: JSON.stringify(dadosProcessos),
        opcaoSelecionada: opcaoSelecionada
      },
      success: function (data) {
        //Recebe o resultado e entra na função
        adicionaExpressao(data.temposServico, data.temposEspera, data.tempoExecucaoFinal, data.tempoEsperaFinal, data.grafico)
      }
    });

  });
});

//A função recebe os parametros e monta um html na tela como uma expressão matemática
function adicionaExpressao(temposServico, temposEspera, tempoExecucaoFinal, tempoEsperaFinal, grafico) {
  const htmlContent = document.getElementById('resultado');
  let numeradorServico = '';
  let numeradorEspera = '';

  //Molda a expressão de acordo com o tamanho dela.
  for (let i = 0; i < temposServico.length; i++) {

    if (i === temposServico.length - 1) {
      numeradorServico += `${temposServico[i]}`;
      numeradorEspera += `${temposEspera[i]}`;
      break;
    }

    numeradorServico += `${temposServico[i]} + `;
    numeradorEspera += `${temposEspera[i]} + `;
  }

  //Monta o html
  const html = `
        <div class="row">
        <p>Os valores não estam na ordem certa</p>
          <div class="col-3">
            <div class="row">
              <div class="col-9">
                <div class="numerador d-flex justify-content-center">
                  ${numeradorServico}
                </div>
                <hr/>
                <div class="denominador d-flex justify-content-center">
                  ${temposServico.length}
                </div>
              </div>
              <div class="col-3">
                =  ${tempoExecucaoFinal}
              </div>
            </div>
            <br>
            <br>
            <div class="row">
              <div class="col-9">
                <div class="numerador d-flex justify-content-center">
                  ${numeradorEspera}
                </div>
                <hr/>
                <div class="denominador d-flex justify-content-center">
                  ${temposEspera.length}
                </div>
              </div>
              <div class="col-3">
                =  ${tempoEsperaFinal}
              </div>
            </div>
          </div>
          <div class="col-9">
            ${grafico}
          </div>
        </div>
        `;

  htmlContent.innerHTML = html;
}




