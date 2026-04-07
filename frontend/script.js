// Arquivo principal de scripts do Frontend (Vanilla JS).
// Responsável por gerenciar as chamadas à API (backend), manipular o DOM (HTML)
// e renderizar as tabelas, estatísticas e projeções de forma dinâmica na tela.

// URL base da nossa API FastAPI. Em produção, isso viria de uma variável de ambiente.
const BASE = 'http://localhost:8000';
// Variável global para armazenar a lista de times e reaproveitá-la entre as abas sem precisar de novas requisições.
window._classTeams = [];

// Função utilitária (Helper) para encurtar a busca de elementos no HTML (semelhante ao jQuery `$('#id')`).
function $(id) { return document.getElementById(id); }

// Exibe notificações flutuantes (Toasts) para dar feedback visual (sucesso/erro) às ações do usuário.
function showToast(msg, type = 'ok') {
  const el = $('toast');
  el.textContent = (type === 'ok' ? '✅ ' : '❌ ') + msg;
  el.className = `toast show ${type}`;
  setTimeout(() => el.className = 'toast', 3800);
}

// Gerencia a navegação entre as abas (SPA - Single Page Application) adicionando/removendo classes CSS 'active'.
function switchTab(el) {
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  el.classList.add('active');
  $(el.dataset.page).classList.add('active');
}

// Wrapper (encapsulador) assíncrono para a API nativa `fetch`.
// Centraliza o tratamento de erros HTTP e a conversão do corpo da resposta para JSON.
async function api(path) {
  const r = await fetch(BASE + path);
  if (!r.ok) throw new Error(`HTTP ${r.status}`);
  return r.json();
}

// Mapeia o índice do array (posição na tabela) para a classe CSS visual da zona de classificação correspondente.
function posClass(i) {
  if (i < 4) return 'g4';
  if (i === 4) return 'g5';
  if (i < 12) return 'g6';
  if (i >= 16) return 'z4';
  return '';
}

// Retorna uma tag HTML formatada (badge) dependendo do texto de status projetado vindo do backend.
function statusLabel(s) {
  if (!s) return '';
  if (s.includes('Campeão')) return `<span style="color:var(--yellow);font-size:10px">🏆</span>`;
  if (s.includes('G4')) return `<span style="color:#60a5fa;font-size:10px">G4</span>`;
  if (s.includes('G5')) return `<span style="color:#93c5fd;font-size:10px">G5</span>`;
  if (s.includes('G6') || s.includes('Sul')) return `<span style="color:#67e8f9;font-size:10px">G6</span>`;
  if (s.includes('Risco')) return `<span style="color:var(--red);font-size:10px">Z4</span>`;
  return `<span style="color:var(--muted);font-size:10px">—</span>`;
}

// ── Status ──────────────────────────────────────
// Pinga a rota raiz do backend para verificar se o servidor está online e atualiza a bolinha de status no Header.
async function checkStatus() {
  try {
    await api('/brasileirao/');
    $('apiDot').classList.add('on');
    $('apiStatus').textContent = 'online';
  } catch {
    $('apiStatus').textContent = 'offline';
  }
}

// ── Sync ────────────────────────────────────────
// Aciona o endpoint de sincronização no backend (que consome a API externa do football-data.org).
// Bloqueia o botão com estado de 'loading' para evitar duplo clique e sobrecarga no banco de dados.
async function syncData() {
  const btn = $('btnSync');
  btn.classList.add('loading');
  btn.textContent = '⟳ Sincronizando...';
  try {
    const d = await api('/brasileirao/sync/dados');
    showToast(d.mensagem || 'Sincronizado!');
    loadAll();
  } catch (e) {
    showToast('Erro: ' + e.message, 'err');
  } finally {
    btn.classList.remove('loading');
    btn.innerHTML = '↻ Sincronizar';
  }
}

// ── ABA 1: Classificação ────────────────────────
// Busca a tabela atualizada localmente e constrói dinamicamente as linhas (<tr>) da tabela HTML.
async function loadClassificacao() {
  try {
    const d = await api('/brasileirao/classificacao');
    const times = d.classificacao || [];
    window._classTeams = times;

    $('k-gols').textContent = d.gols_campeonato ?? '—';
    $('k-partidas').textContent = Math.round(d.partidas_registradas || 0) || '—';
    $('k-media').textContent = d['média_gols_por_partida'] ?? '—';
    $('k-rodada').textContent = times[0]?.jogos ?? '—';
    $('k-times').textContent = times.length || '—';
    $('season-chip').textContent = times[0]?.temporada ? 'Temporada ' + times[0].temporada : '—';

    const sepAfter = { 3: 'g4', 4: 'g5', 11: 'g6', 15: 'mt' };
    const sepColor = { g4: '#1a3a5c', g5: '#1a325c', g6: '#1a3040', mt: '#1e2820' };

    $('classBody').innerHTML = times.map((t, i) => {
      const pc = posClass(i);
      const sg = t.saldo_gols;
      const sgC = sg > 0 ? 'pos' : sg < 0 ? 'neg' : 'zer';
      const sgS = sg > 0 ? '+' + sg : String(sg);

      let html = `<tr>
    <td><span class="pos-badge ${pc}">${t.posicao}</span></td>
    <td><span class="team-nm">${t.nome_time}</span></td>
    <td class="pts-val">${t.pontos}</td>
    <td class="dim-val">${t.jogos}</td>
    <td style="color:var(--green);font-family:var(--mono);font-size:12px">${t.vitorias}</td>
    <td style="color:var(--yellow);font-family:var(--mono);font-size:12px">${t.empates}</td>
    <td style="color:var(--red);font-family:var(--mono);font-size:12px">${t.derrotas}</td>
    <td class="dim-val">${t.gols_feitos}</td>
    <td class="dim-val">${t.gols_sofridos}</td>
    <td><span class="saldo-val ${sgC}">${sgS}</span></td>
  </tr>`;

      if (sepAfter[i] !== undefined) {
        html += `<tr class="zone-sep" style="--sep-color:${sepColor[sepAfter[i]]}"><td colspan="10"></td></tr>`;
      }
      return html;
    }).join('');

  } catch (e) {
    $('classBody').innerHTML = `<tr><td colspan="10">
      <div class="empty"><div class="eicon">📭</div><p>Sem dados. Clique em <strong>Sincronizar</strong>.</p></div>
    </td></tr>`;
  }
}

// ── ABA 2: Projeções ─────────────────────────────
// O "coração" preditivo do Frontend. Cruza dados de diferentes rotas da API em uma única visão unificada.
async function loadProjecoes() {
  try {
    // Executa as 3 requisições em paralelo (Promise.all) para melhorar drasticamente a performance de carregamento.
    const [dTend, dFreq, dPower] = await Promise.all([
      api('/brasileirao/tendencia'),
      api('/brasileirao/tendencia/frequencia'),
      api('/brasileirao/power-ranking'),
    ]);

    // Campeão por média
    const ins = dTend.insight_de_tendencia;
    $('ic-campeao-media').textContent = ins.campeao_previsto;
    $('ic-msg-media').textContent = ins.mensagem;

    // Campeão por frequência
    const campeaoFreq = dFreq.previsao_campeao;
    $('ic-campeao-freq').textContent = campeaoFreq;

    // Criação de dicionários (Lookups) indexados pelo nome do time (O(1) lookup time) para cruzar os dados facilmente na montagem da tabela.
    const freqMap = {};
    (dFreq.tabela_projetada || []).forEach(t => { freqMap[t.time] = t; });
    const powerMap = {};
    (dPower || []).forEach(t => { powerMap[t.time] = t; });

    // Insight de frequência para o campeão
    const fqCamp = freqMap[campeaoFreq];
    if (fqCamp) {
      $('ic-msg-freq').textContent =
        `Projeção de ${Number(fqCamp.projecao_final_38_rodadas).toFixed(0)} pts com ${fqCamp.frequencia_vitoria} de taxa de vitória.`;
    }

    // Renderização da tabela unificada. Combina a 'tendência média' com a 'frequência' e exibe os deltas (diferenças).
    const analise = dTend.analise_detalhada || [];
    $('projBody').innerHTML = analise.map(t => {
      const ptsMedia = Number(t.tendencia_final_38_rodadas).toFixed(0);
      const fq = freqMap[t.time];
      const pw = powerMap[t.time];

      const ptsFreq = fq ? Number(fq.projecao_final_38_rodadas).toFixed(0) : '—';
      const freqVit = fq ? fq.frequencia_vitoria : '—';

      // Δ entre os dois métodos
      let diffHtml = '<span class="diff-badge eq">—</span>';
      if (fq) {
        const diff = Number(ptsFreq) - Number(ptsMedia);
        const ac = diff > 1 ? 'up' : diff < -1 ? 'dn' : 'eq';
        const as = diff > 0 ? `+${diff.toFixed(0)}` : diff.toFixed(0);
        diffHtml = `<span class="diff-badge ${ac}">${as}</span>`;
      }

      // Power
      const pwScore = pw ? pw.score : '—';
      const pwPos = pw ? pw.posicao_forca : '—';
      let deltaHtml = '<span class="delta-cell eq">—</span>';
      if (pw && pw.delta !== null) {
        const dc = pw.delta > 0 ? 'up' : pw.delta < 0 ? 'dn' : 'eq';
        const ds = pw.delta > 0 ? `▲${Math.abs(pw.delta)}` : pw.delta < 0 ? `▼${Math.abs(pw.delta)}` : `=`;
        deltaHtml = `<span class="delta-cell ${dc}">${ds}</span>`;
      }

      return `<tr>
    <td style="color:var(--muted);font-family:var(--mono);font-size:11px">${t.posicao_atual}</td>
    <td style="font-weight:500;font-size:13px">${t.time}</td>
    <td class="sep" style="font-family:var(--mono);font-size:11px;color:var(--muted2)">${t.aproveitamento}</td>
    <td class="proj-pts">${ptsMedia}</td>
    <td>${statusLabel(t.status_projetado)}</td>
    <td class="sep" style="font-family:var(--mono);font-size:11px;color:var(--muted2)">${freqVit}</td>
    <td class="proj-pts2">${ptsFreq}</td>
    <td>${diffHtml}</td>
    <td class="sep power-score-cell">${pwScore}</td>
    <td style="font-family:var(--mono);font-size:12px;color:var(--muted2)">${pwPos}°</td>
    <td>${deltaHtml}</td>
  </tr>`;
    }).join('');

    // Top 4 Power sidebar
    $('miniPower').innerHTML = (dPower || []).slice(0, 4).map(t => {
      const dc = t.delta < 0 ? 'up' : t.delta > 0 ? 'dn' : 'eq';
      const ds = t.delta < 0 ? `▲${Math.abs(t.delta)} acima` : t.delta > 0 ? `▼${t.delta} abaixo` : `na posição esperada`;
      return `<div class="mini-rank-item">
    <div class="mini-rank-pos">${t.posicao_forca}</div>
    <div class="mini-rank-info">
      <div class="mini-rank-name">${t.time}</div>
      <div class="mini-rank-meta"> Atk ${t.ataque} · Def ${t.defesa} · Atual Pos: <span class="delta-cell ${dc}" style="font-size:10px">${ds}</span></div>
    </div>
    <div class="mini-rank-score">${t.score}</div>
  </div>`;
    }).join('');

    // Top 4 LOSS Power sidebar
    $('miniLossPower').innerHTML = (dPower || []).slice(16, 20).map(t => {
      const dc = t.delta < 0 ? 'up' : t.delta > 0 ? 'dn' : 'eq';
      const ds = t.delta < 0 ? `▲${Math.abs(t.delta)} acima` : t.delta > 0 ? `▼${t.delta} abaixo` : `na posição esperada`;
      return `<div class="mini-rank-item">
    <div class="mini-rank-pos">${t.posicao_forca}</div>
    <div class="mini-rank-info">
      <div class="mini-rank-name">${t.time}</div>
      <div class="mini-rank-meta"> Atk ${t.ataque} · Def ${t.defesa} · Atual Pos: <span class="delta-cell ${dc}" style="font-size:10px">${ds}</span></div>
    </div>
    <div class="mini-rank-score">${t.score}</div>
  </div>`;
    }).join('');

  } catch (e) {
    console.error(e);
    $('projBody').innerHTML = `<tr><td colspan="11">
    <div class="empty"><div class="eicon">📭</div><p>Dados indisponíveis</p></div>
  </td></tr>`;
  }
}

// ── ABA 3: Estatísticas ──────────────────────────
// Puxa estatísticas globais e as renderiza em formato de cards, listas e barras de progresso.
async function loadEstatisticas() {
  try {
    const d = await api('/brasileirao/estatisticas/reais');
    const pan = d.panorama_geral;
    const ext = d.extremos_do_campeonato;
    const zon = d.zonas_atuais;
    const rank = d.rankings;

    $('es-gols').textContent = pan.total_gols;
    $('es-partidas').textContent = pan.total_partidas_registradas;
    $('es-rodada').textContent = pan.rodada_media_atual;

    // Mapeamento e renderização dinâmica dos extremos (melhor ataque, pior defesa, líder, etc.)
    $('extremosWrap').innerHTML = [
      { icon: '👑', label: 'Líder', team: ext.lider, val: '1º colocado' },
      { icon: '⚠️', label: 'Lanterna', team: ext.lanterna, val: 'último' },
      { icon: '🥇', label: 'Mais Vitórias', team: ext.maior_vitorioso.time, val: ext.maior_vitorioso.valor + ' V' },
      { icon: '🤝', label: 'Mais Empates', team: ext.o_que_mais_empata.time, val: ext.o_que_mais_empata.valor + ' E' },
      { icon: '😢', label: 'Mais Derrotas', team: ext.o_que_mais_perdeu.time, val: ext.o_que_mais_perdeu.valor + ' D' },
      { icon: '⚽', label: 'Melhor Ataque', team: ext.melhor_ataque.time, val: ext.melhor_ataque.gols + ' gols' },
      { icon: '🛡️', label: 'Pior Defesa', team: ext.pior_defesa.time, val: ext.pior_defesa.gols + ' sofridos' },
    ].map(e => `
  <div class="extremo-row">
    <div class="extremo-left">
      <div class="extremo-icon">${e.icon}</div>
      <div>
        <div class="extremo-label">${e.label}</div>
        <div class="extremo-team">${e.team}</div>
      </div>
    </div>
    <div class="extremo-val">${e.val}</div>
  </div>`).join('');

    // Zonas — monta set dos times com zona definida e deduz o meio de tabela
    // (Usando Set para buscas otimizadas de O(1))
    const allZoned = new Set([
      ...(zon.G4_Libertadores || []),
      ...(zon.G5_Pre_Libertadores || []),
      ...(zon.G6_Sul_Americana || []),
      ...(zon.Z4_Rebaixamento || []),
    ]);
    const midTeams = window._classTeams
      .filter(t => !allZoned.has(t.nome_time))
      .map(t => t.nome_time);

    const zoneDefs = [
      { teams: zon.G4_Libertadores || [], cls: 'g4', color: '#1a3a5c', title: 'G4 — Libertadores', sub: 'Fase de grupos · 1º ao 4º' },
      { teams: zon.G5_Pre_Libertadores || [], cls: 'g5', color: '#1a325c', title: 'G5 — Pré-Libertadores', sub: '5º colocado' },
      { teams: zon.G6_Sul_Americana || [], cls: 'g6', color: '#1a3040', title: 'G6 — Sul-Americana', sub: '6º ao 12º' },
      { teams: midTeams, cls: 'mt', color: '#243028', title: 'Meio de Tabela', sub: '13º ao 16º' },
      { teams: zon.Z4_Rebaixamento || [], cls: 'z4', color: '#4a1a22', title: 'Z4 — Rebaixamento', sub: 'Últimos 4' },
    ];

    $('zonesWrap').innerHTML = zoneDefs.map(z => `
  <div class="zone-block">
    <div class="zone-block-head">
      <div class="zone-color-bar" style="background:${z.color}"></div>
      <div>
        <div class="zone-block-title" style="color:${z.color}">${z.title}</div>
        <div class="zone-block-sub">${z.sub}</div>
      </div>
    </div>
    <div class="zone-teams-row">
      ${z.teams.map(t => `<span class="zone-team-pill ${z.cls}">${t}</span>`).join('')
      || '<span style="color:var(--muted);font-size:12px">—</span>'}
    </div>
  </div>`).join('');

    // Montagem do gráfico de barras horizontais do Top 4 Ataques. Calcula a % de preenchimento (width) dinamicamente.
    const maxGF = Math.max(...rank.top_4_goleadores.map(t => t.gols_feitos));
    $('rankAtaque').innerHTML = rank.top_4_goleadores.map((t, i) => `
  <div class="rank-bar-item">
    <div class="rank-bar-pos" style="color:var(--green)">${i + 1}</div>
    <div class="rank-bar-body">
      <div class="rank-bar-top">
        <span class="rank-bar-name">${t.nome}</span>
        <span class="rank-bar-val" style="color:var(--green)">${t.gols_feitos} gols</span>
      </div>
      <div class="bar-track">
        <div class="bar-fill" style="width:${(t.gols_feitos / maxGF * 100).toFixed(1)}%;background:var(--green)"></div>
      </div>
      <div class="rank-bar-sub">${t.media_gol_por_partida} gols/jogo</div>
    </div>
  </div>`).join('');

    // Montagem do gráfico de barras horizontais do Top 4 Defesas (com cor invertida/vermelha para representar perigo).
    const maxGS = Math.max(...rank.top_4_mais_tomam_gols.map(t => t.gols_sofridos));
    $('rankDefesa').innerHTML = rank.top_4_mais_tomam_gols.map((t, i) => `
  <div class="rank-bar-item">
    <div class="rank-bar-pos" style="color:var(--red)">${i + 1}</div>
    <div class="rank-bar-body">
      <div class="rank-bar-top">
        <span class="rank-bar-name">${t.nome}</span>
        <span class="rank-bar-val" style="color:var(--red)">${t.gols_sofridos} gols sofridos</span>
      </div>
      <div class="bar-track">
        <div class="bar-fill" style="width:${(t.gols_sofridos / maxGS * 100).toFixed(1)}%;background:var(--red)"></div>
      </div>
      <div class="rank-bar-sub">${t.media_gol_por_partida} gols sofridos/jogo</div>
    </div>
  </div>`).join('');

  } catch (e) {
    console.error(e);
  }
}

// ── ABA 4: Simulações ─────────────────────────────
// Monte Carlo + Previsão Avançada em paralelo
async function loadSimulacoes() {
  try {
    const [dMC, dAv] = await Promise.all([
      api('/brasileirao/previsao/monte-carlo'),
      api('/brasileirao/tendencia/avancada'),
    ]);

    // KPIs Monte Carlo
    const mc = dMC.previsao || [];
    const favTitulo = mc[0];
    const favG4 = [...mc].sort((a, b) => b['chance_g4_%'] - a['chance_g4_%'])[0];
    const favZ4 = [...mc].sort((a, b) => b['chance_rebaixamento_%'] - a['chance_rebaixamento_%'])[0];

    if (favTitulo) {
      $('mc-fav-titulo').textContent = favTitulo.time;
      $('mc-fav-titulo-pct').textContent = favTitulo['chance_titulo_%'].toFixed(1) + '% de chance';
    }
    if (favG4) {
      $('mc-fav-g4').textContent = favG4.time;
      $('mc-fav-g4-pct').textContent = favG4['chance_g4_%'].toFixed(1) + '% de chance';
    }
    if (favZ4) {
      $('mc-fav-z4').textContent = favZ4.time;
      $('mc-fav-z4-pct').textContent = favZ4['chance_rebaixamento_%'].toFixed(1) + '% de chance';
    }

    // Tabela Monte Carlo
    const maxTitulo = Math.max(...mc.map(t => t['chance_titulo_%']));
    const maxG4 = Math.max(...mc.map(t => t['chance_g4_%']));
    const maxZ4 = Math.max(...mc.map(t => t['chance_rebaixamento_%']));

    $('mcBody').innerHTML = mc.map((t, i) => {
      const pctTitulo = t['chance_titulo_%'];
      const pctG4 = t['chance_g4_%'];
      const pctZ4 = t['chance_rebaixamento_%'];

      const barTitulo = `<div class="mc-pct-bar">
        <div class="mc-pct-track"><div class="mc-pct-fill" style="width:${(pctTitulo / maxTitulo * 100).toFixed(1)}%;background:var(--yellow)"></div></div>
        <span class="mc-pct-label" style="color:var(--yellow)">${pctTitulo.toFixed(1)}%</span>
      </div>`;

      const barG4 = `<div class="mc-pct-bar">
        <div class="mc-pct-track"><div class="mc-pct-fill" style="width:${(pctG4 / maxG4 * 100).toFixed(1)}%;background:#60a5fa"></div></div>
        <span class="mc-pct-label" style="color:#60a5fa">${pctG4.toFixed(1)}%</span>
      </div>`;

      const barZ4 = `<div class="mc-pct-bar">
        <div class="mc-pct-track"><div class="mc-pct-fill" style="width:${pctZ4 > 0 ? (pctZ4 / maxZ4 * 100).toFixed(1) : 0}%;background:var(--red)"></div></div>
        <span class="mc-pct-label" style="color:var(--red)">${pctZ4.toFixed(1)}%</span>
      </div>`;

      return `<tr>
        <td style="color:var(--muted);font-family:var(--mono);font-size:11px">${i + 1}</td>
        <td>${t.time}</td>
        <td style="font-family:var(--mono);font-size:13px;font-weight:700;color:var(--green)">${t.pontos_medios.toFixed(0)}</td>
        <td style="min-width:120px">${barTitulo}</td>
        <td style="min-width:120px">${barG4}</td>
        <td style="min-width:120px">${barZ4}</td>
      </tr>`;
    }).join('');

    // Previsão Avançada
    $('avancada-metodologia').textContent = dAv.metodologia || '';

    const previsao = dAv.previsao || [];
    $('avBody').innerHTML = previsao.map(t => {
      const dc = t.delta < 0 ? 'up' : t.delta > 0 ? 'dn' : 'eq';
      const ds = t.delta < 0 ? `▲${Math.abs(t.delta)}` : t.delta > 0 ? `▼${t.delta}` : `=`;
      return `<tr>
        <td style="font-family:var(--mono);font-size:11px;color:var(--muted2)">${t.posicao_real}°</td>
        <td>${t.time}</td>
        <td style="font-family:var(--mono);font-size:12px;color:var(--muted2)">${t.pontos_atuais}</td>
        <td style="font-family:var(--mono);font-size:14px;font-weight:700;color:var(--cyan)">${t.projecao_final.toFixed(0)}</td>
        <td style="font-family:var(--mono);font-size:12px;color:var(--muted2)">${t.posicao_projetada}°</td>
        <td><span class="delta-cell ${dc}" style="font-size:12px">${ds}</span></td>
      </tr>`;
    }).join('');

  } catch (e) {
    console.error(e);
    $('mcBody').innerHTML = `<tr><td colspan="6"><div class="empty"><div class="eicon">📭</div><p>Dados indisponíveis</p></div></td></tr>`;
    $('avBody').innerHTML = `<tr><td colspan="6"><div class="empty"><div class="eicon">📭</div><p>Dados indisponíveis</p></div></td></tr>`;
  }
}

// ── ABA 5: Próximos Jogos ─────────────────────────
async function loadProximosJogos() {
  try {
    const d = await api('/brasileirao/proximos-jogos');
    const rodadas = d.rodadas || [];

    rodadas.sort((a, b) => a.numero - b.numero);

    $('pj-total').textContent = d.total_jogos || '—';
    $('pj-proxima-rodada').textContent = rodadas[0] ? `R${rodadas[0].numero}` : '—';
    $('pj-rodadas-count').textContent = rodadas.length || '—';

    if (rodadas.length === 0) {
      $('jogosContainer').innerHTML = `
        <div class="empty">
          <div class="eicon">📭</div>
          <p>Nenhum jogo agendado.</p>
        </div>`;
      return;
    }

    $('jogosContainer').innerHTML = rodadas.map((rodadaObj, idx) => {
      const jogos = rodadaObj.jogos || [];
      const rodadaNumero = rodadaObj.numero;
      const isOpen = idx === 0 ? 'open' : '';

      const jogosHtml = jogos.map(j => {
        let dataLabel = j.data;

        try {
          const parts = j.data.split('-');
          if (parts.length === 3) {
            const [dia, mes, ano] = parts;

            const dt = new Date(ano, mes - 1, dia);

            dataLabel = dt.toLocaleDateString('pt-BR', {
              weekday: 'short',
              day: '2-digit',
              month: 'short'
            });
          }
        } catch { }

        console.log(j.data, '=>', dataLabel);

        return `
          <div class="jogo-row">
            <div class="jogo-mandante">${j.mandante}</div>
            <div class="jogo-vs">
              <div class="jogo-vs-badge">
                <span class="jogo-vs-text">VS</span>
                <span class="jogo-hora">${j.hora}</span>
                <span class="jogo-data">${dataLabel}</span>
              </div>
            </div>
            <div class="jogo-visitante">${j.visitante}</div>
          </div>
        `;
      }).join('');

      return `
        <div class="rodada-block">
          <div class="rodada-header" onclick="toggleRodada(this)">
            <span class="rodada-title">Rodada ${rodadaNumero}</span>
            <div style="display:flex;align-items:center;gap:12px">
              <span class="rodada-count">
                ${jogos.length} jogo${jogos.length !== 1 ? 's' : ''}
              </span>
              <span class="rodada-toggle ${isOpen}">▾</span>
            </div>
          </div>
          <div class="rodada-jogos ${isOpen}">
            ${jogosHtml}
          </div>
        </div>
      `;
    }).join('');

  } catch (e) {
    console.error(e);
    $('jogosContainer').innerHTML = `
      <div class="empty">
        <div class="eicon">📭</div>
        <p>Dados indisponíveis. Clique em <strong>Sincronizar</strong>.</p>
      </div>`;
  }
}

// Toggle das rodadas (accordion)
function toggleRodada(el) {
  const jogos = el.nextElementSibling;
  const toggle = el.querySelector('.rodada-toggle');
  jogos.classList.toggle('open');
  toggle.classList.toggle('open');
}

// ── Init ─────────────────────────────────────────
// Ponto de entrada (Entry point) de dados. Carrega todas as métricas em paralelo assim que a página renderiza.
function loadAll() {
  loadClassificacao();
  loadProjecoes();
  loadEstatisticas();
  loadSimulacoes();
  loadProximosJogos();
}

checkStatus();
loadAll();