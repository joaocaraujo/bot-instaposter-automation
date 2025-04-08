# Automação de Postagens no Instagram

O objetivo deste projeto é automatizar um processo manual feito diariamente(by myself) para melhorar a eficiência e gestão de tempo. Este projeto foi desenvolvido de forma personalizada para atender minhas próprias expectativas e necessidades específicas, sem a intenção de ser reutilizado por terceiros.

Este script automatiza o processo de postagem no Instagram, permitindo postar múltiplas imagens com suas respectivas descrições.

## Requisitos

- Python 3.7 ou superior
- Chrome instalado
- Conta no Instagram

## Instalação

1. Instale as dependências:
```bash
pip install -r requirements.txt
```

2. Prepare seus arquivos:
   - Coloque todas as imagens em uma pasta (formato PNG)
   - Crie um arquivo de texto com as descrições base (formato conforme exemplo)

## Como Usar

1. Execute o script:
```bash
python instagram_poster.py
```

2. O script irá:
   - Fazer login automaticamente usando seu perfil do Chrome
   - Postar as imagens em ordem numérica
   - Adicionar as descrições automaticamente
   - Marcar os usuários mencionados nos textos
   - Remover as imagens após postagem
   - Remover os textos usados do arquivo
   - Limpar o arquivo zgpttextos.txt ao final

## Formato do Arquivo de Textos

### Arquivo textobase.txt
```
Texto @usuario1

📍 Endereço
📱 Telefone
.
.
.
.
.
#hashtags

Texto @usuario2
...
```

## Observações

- As imagens devem estar numeradas em ordem crescente (ex: 1.png, 2.png, etc.)
- O script irá postar automaticamente sem pedir confirmação
- Em caso de erro, o script mostrará a mensagem e permitirá continuar com a próxima imagem
- O script limpa automaticamente:
  - As imagens após serem postadas
  - Os textos usados do arquivo textobase.txt
  - O arquivo zgpttextos.txt ao final do processo
- Certifique-se de que todas as imagens e textos estejam na ordem correta 