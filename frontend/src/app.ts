import { io } from 'socket.io-client'

import { Terminal } from 'xterm'
import { FitAddon } from 'xterm-addon-fit'
import 'xterm/css/xterm.css'

import './app.scss'

const socket = io(`:${import.meta.env.VITE_BACKEND_PORT}`)

const term = new Terminal({
  cursorBlink: true,
  cols: import.meta.env.VITE_TERM_WIDTH,
  rows: import.meta.env.VITE_TERM_HEIGHT,
})
const fitAddon = new FitAddon()
let command = ''

term.open(document.getElementById('app')!)

function prompt() {
  command = ''
  term.write('\r\n')
}

function init() {
  // Terminal
  term.loadAddon(fitAddon)
  fitAddon.fit()
  term.onData((e) => {
    switch (e) {
      case '\r': // Enter
        socket.emit('ask_command', command)
        prompt()
        break

      case '\u007F': // Backspace (DEL)
        if (command.length > 0) {
          term.write('\b \b')
          command = command.slice(0, -1)
        }
        break

      default:
        if (
          (e >= String.fromCharCode(0x20) && e <= String.fromCharCode(0x7e)) ||
          e >= '\u00a0'
        ) {
          command += e
          term.write(e)
        }
        break
    }
  })
  prompt()

  // Socket
  socket.on('answer_flush', () => {
    prompt()
  })

  socket.on(
    'answer_settitle',
    ({
      continuous,
      commandname,
    }: {
      continuous: boolean
      commandname: string
    }) => {
      if (continuous) {
        term.write(commandname)
        prompt()
      } else {
        document.getElementById('commandname')!.innerText = commandname
      }
    },
  )

  socket.on('answer_command', (data: string) => {
    term.write(data.replace(/\n/g, '\r\n'))
  })
}

init()
onresize = () => {
  fitAddon.fit()
}
