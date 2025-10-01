# Atividades de Plataformas de Distribuição

## 📌 Atividade 01 – Cliente-Servidor TCP
Implemente uma aplicação **cliente-servidor** usando **socket TCP** para coletar e exibir, em tempo quase real, métricas de desempenho de vários computadores.  

- Cada **cliente** atua como um agente instalado em uma máquina a ser monitorada.  
- Ele coleta periodicamente dados de apenas **um recurso**:  
  - CPU (percentual de ocupação por núcleo e média geral),  
  - Memória (total, utilizada, livre),  
  - Disco (uso de espaço, taxa de leitura/escrita),  
  - Rede (taxa de upload/download, pacotes perdidos).  
- As informações são enviadas em intervalos configuráveis (ex.: a cada 5 segundos) para o **servidor**.  
- O **servidor** mantém conexões persistentes com todos os agentes, armazena os dados em memória e mantém uma lista dos clientes conectados.

---

## 📌 Atividade 02 – Cliente-Servidor UDP
Reimplemente a aplicação anterior utilizando **socket UDP**, adaptando o envio e recepção de mensagens sem a necessidade de conexões persistentes.  

O objetivo é comparar o comportamento entre **TCP (confiável, orientado a conexão)** e **UDP (rápido, sem conexão)** no envio de métricas em tempo real.

## 📌 Atividade 03 – Cliente-Servidor Protocolo HTTP 

A atividade 03 no caso seria refazer os outros dois client server agora usando o protocolo http 
