import * as THREE from 'three';
export function createUnderwater(canvas: HTMLCanvasElement) {
  const renderer = new THREE.WebGLRenderer({canvas, antialias: false, powerPreference:'low-power'});
  renderer.setPixelRatio(Math.min(devicePixelRatio, 1.5));
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  const scene = new THREE.Scene();
  scene.background = new THREE.Color('#063c4b');
  scene.fog = new THREE.FogExp2('#064351', .035);
  const camera = new THREE.PerspectiveCamera(52, 1, .1, 180);
  camera.position.set(0, 7, 28); camera.lookAt(0, 2, -8);
  scene.add(new THREE.HemisphereLight('#b1eaf0', '#15382c', 2));
  const sun = new THREE.DirectionalLight('#d2fff4', 3); sun.position.set(-10,30,8); scene.add(sun);
  const seabed = new THREE.PlaneGeometry(160, 160, 80, 80);
  const positions = seabed.attributes.position;
  for (let i=0;i<positions.count;i++) { const x=positions.getX(i), y=positions.getY(i); positions.setZ(i, Math.sin(x*.15)*1.1 + Math.cos(y*.12)*.7 + Math.sin(x*.6+y*.4)*.12); }
  seabed.computeVertexNormals();
  const floor = new THREE.Mesh(seabed,new THREE.MeshStandardMaterial({color:'#697e65',roughness:1})); floor.rotation.x=-Math.PI/2; floor.position.y=-4; scene.add(floor);
  // Environment geometry only; no fish proxies are represented as production assets.
  const rocks = new THREE.InstancedMesh(new THREE.IcosahedronGeometry(1,2),new THREE.MeshStandardMaterial({color:'#405e58',roughness:1}),45);
  const dummy = new THREE.Object3D();
  for(let i=0;i<45;i++){const x=Math.sin(i*42.7)*40,z=-6-Math.abs(Math.cos(i*18.4))*65; dummy.position.set(x,-3.2,z);dummy.scale.set(1+i%4,1+(i%3)*.5,1+i%5);dummy.rotation.set(i*.2,i,0);dummy.updateMatrix();rocks.setMatrixAt(i,dummy.matrix);}scene.add(rocks);
  const rayGeometry = new THREE.PlaneGeometry(4,55);
  const rayMaterial = new THREE.MeshBasicMaterial({color:'#a1efda',transparent:true,opacity:.045,depthWrite:false,side:THREE.DoubleSide,blending:THREE.AdditiveBlending});
  for(let i=0;i<7;i++){const ray=new THREE.Mesh(rayGeometry,rayMaterial);ray.position.set(-26+i*8,15,-22-i*3);ray.rotation.z=-.3;scene.add(ray);}
  const motesGeometry=new THREE.BufferGeometry(); const points=new Float32Array(600*3);
  for(let i=0;i<points.length;i++)points[i]=Math.sin(i*127.1)* (i%3===1?18:55);
  motesGeometry.setAttribute('position',new THREE.BufferAttribute(points,3));
  const motes=new THREE.Points(motesGeometry,new THREE.PointsMaterial({size:.055,color:'#c5f2df',transparent:true,opacity:.45,depthWrite:false}));scene.add(motes);
  let lost=false;
  canvas.addEventListener('webglcontextlost', event=>{event.preventDefault();lost=true;canvas.dataset.calls='0';canvas.dataset.status='context-lost';});
  canvas.addEventListener('webglcontextrestored',()=>{lost=false;canvas.dataset.status='ready';});
  const resize=()=>{renderer.setSize(innerWidth,innerHeight,false);camera.aspect=innerWidth/innerHeight;camera.updateProjectionMatrix();};
  window.addEventListener('resize',resize);resize();
  return {render(time:number){if(lost)return; motes.rotation.y=time*.007;camera.position.x=Math.sin(time*.08)*.45;camera.lookAt(0,2,-8); renderer.render(scene,camera);canvas.dataset.status='ready';canvas.dataset.calls=String(renderer.info.render.calls);},dispose(){window.removeEventListener('resize',resize);scene.traverse(o=>{if(o instanceof THREE.Mesh || o instanceof THREE.Points){o.geometry.dispose();const materials=Array.isArray(o.material)?o.material:[o.material];materials.forEach(m=>m.dispose());}});renderer.dispose();}};
}
