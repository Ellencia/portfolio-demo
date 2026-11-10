// Offline rendering of the existing four-part arrangement. Build-time only.
// Usage: node ocr/render_bgm.cjs <js-synthesizer directory> <FluidR3 .sf3> <events.json> <out.wav>
const fs = require('node:fs');
const path = require('node:path');
const [lib, font, input, output] = process.argv.slice(2);
const fluid = require(path.resolve(lib, 'externals/libfluidsynth-2.4.6-with-libsndfile.js'));
const JSSynth = require(path.resolve(lib));
JSSynth.Synthesizer.initializeWithFluidSynthModule(fluid);
(async () => {
  await JSSynth.waitForReady();
  const data = JSON.parse(fs.readFileSync(input, 'utf8'));
  const sr = 48000, synth = new JSSynth.Synthesizer();
  synth.init(sr);
  const bytes = fs.readFileSync(font);
  const sf = await synth.loadSFont(bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset+bytes.byteLength));
  data.parts.forEach(([program,volume],ch) => {
    synth.midiProgramSelect(ch,sf,0,program);
    synth.midiControl(ch,7,volume); synth.midiControl(ch,91,0); synth.midiControl(ch,93,0);
  });
  const count = Math.ceil(data.seconds*sr), pcm = Buffer.alloc(count*4);
  let pos = 0;
  function renderTo(end) {
    while (pos < end) {
      const n = Math.min(4096,end-pos), out = [new Float32Array(n),new Float32Array(n)];
      synth.render(out);
      for(let i=0;i<n;i++) for(let ch=0;ch<2;ch++)
        pcm.writeInt16LE(Math.round(Math.max(-1,Math.min(1,out[ch][i]))*32767),(pos+i)*4+ch*2);
      pos += n;
    }
  }
  for (const [time,ch,note,vel] of data.events) {
    const frame = Math.min(count,Math.round(time*sr)); renderTo(frame);
    if (vel) synth.midiNoteOn(ch,note,vel); else synth.midiNoteOff(ch,note);
  }
  renderTo(count); synth.close();
  const h=Buffer.alloc(44); h.write('RIFF'); h.writeUInt32LE(pcm.length+36,4); h.write('WAVEfmt ',8);
  h.writeUInt32LE(16,16);h.writeUInt16LE(1,20);h.writeUInt16LE(2,22);h.writeUInt32LE(sr,24);
  h.writeUInt32LE(sr*4,28);h.writeUInt16LE(4,32);h.writeUInt16LE(16,34);h.write('data',36);h.writeUInt32LE(pcm.length,40);
  fs.writeFileSync(output,Buffer.concat([h,pcm])); console.log(output,count/sr+' seconds, four MIDI channels');
})().catch(e=>{console.error(e);process.exitCode=1;});
