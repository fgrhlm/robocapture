const Hooks = Object.freeze({
  OPEN: "open",
  CLOSE: "close",
  ERROR: "error",
  MESSAGE: "message"
})

class Callback {
  constructor(hook, func){
    this.hook = hook
    this.func = func
  }
}

class Client {
  constructor(host, port, cb){
    this.socket = new WebSocket(`ws://${host}:${port}`);

    this.callbacks = {}

    cb.forEach(n => {
      switch(n.hook){
        case Hooks.OPEN:
          this.callbacks[Hooks.OPEN] = n;
          break
        case Hooks.CLOSE:
          this.callbacks[Hooks.CLOSE] = n;
          break
        case Hooks.ERROR:
          this.callbacks[Hooks.ERROR] = n;
          break
        case Hooks.MESSAGE:
          this.callbacks[Hooks.MESSAGE] = n;
          break
        default:
          break
      }
    })

    // Events
    this.socket.addEventListener("open", e => {
      console.log(`Connection established: ${host}:${port}`);

      this.execCallback(Hooks.OPEN, e);
    });

    this.socket.addEventListener("close", e => {
      console.log(`Connection closed: ${host}:${port}`);

      this.execCallback(Hooks.CLOSE, e);
    });

    this.socket.addEventListener("error", e => {
      console.error(`Error: ${e}`);
      this.execCallback(Hooks.ERROR, e);
    });

    this.socket.addEventListener("message", e => {
      this.execCallback(Hooks.MESSAGE, e);
    });
  }

  execCallback(hook, event){
    if(this.callbacks[hook] === undefined) return;

    try {
      this.callbacks[hook].func(event);
    } catch(err) {
      console.error(`Callback '${hook}' failed: ${err} -- ${event.data}`)
    }
  }
}

export { Client, Hooks, Callback };
