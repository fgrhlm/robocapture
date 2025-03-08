class RoboCapture {
  constructor(host, port, callback){
    this.socket = new WebSocket(`ws://${host}:${port}`); 
    this.data = []
    this.callback = callback

    // Socket Events
    this.socket.addEventListener("open", e => {
      console.log(`Connection established: ${host}:${port}`);
    });

    this.socket.addEventListener("close", e => {
      console.log(`Connection closed: ${host}:${port}`);
    });

    this.socket.addEventListener("message", e => {
      this.data = JSON.parse(e.data);
      try {
        this.callback(data); 
      } catch (err) {
        console.error(`Callback failed: ${err}`)
      }
    });
  }
}

export default RoboCapture
