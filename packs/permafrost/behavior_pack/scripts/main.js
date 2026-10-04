import { world, system, BlockPermutation, GameMode, ItemStack } from "@minecraft/server";
const SNOW = "classic_permafrost:snow_layer", ICE = "classic_permafrost:ice";
const scans = new Map();
const columns=[];
for(let x=-16;x<=16;x++)for(let z=-16;z<=16;z++)columns.push([x,z]);
columns.sort((a,b)=>a[0]*a[0]+a[1]*a[1]-b[0]*b[0]-b[1]*b[1]);
let reverting=false;
function safeGet(dim,l){try{return dim.getBlock(l);}catch{return undefined;}}
function convert(block){
 if(!block)return;
 if(reverting){
  if(block.typeId===SNOW)block.setPermutation(BlockPermutation.resolve("minecraft:snow_layer",{height:block.permutation.getState("classic_permafrost:layers")-1}));
  else if(block.typeId===ICE)block.setType("minecraft:ice");
  return;
 }
 if(block.typeId==="minecraft:snow_layer"){
  const height=block.permutation.getState("height") ?? 0;
  block.setPermutation(BlockPermutation.resolve(SNOW,{"classic_permafrost:layers":Math.min(8,Math.max(1,height+1))}));
 }else if(block.typeId==="minecraft:ice")block.setType(ICE);
}
world.afterEvents.playerPlaceBlock.subscribe(({block})=>{try{convert(block);}catch(error){console.warn(`[Permafrost] ${error}`);}});
// Preserve stacking when the player adds snow on top of a protected layer.
world.beforeEvents.playerInteractWithBlock.subscribe(event=>{
 if(reverting || event.block.typeId!==SNOW || event.itemStack?.typeId!=="minecraft:snow_layer")return;
 const layers=event.block.permutation.getState("classic_permafrost:layers");
 if(layers>=8)return;
 event.cancel=true;
 const dim=event.block.dimension,l={...event.block.location},player=event.player;
 system.run(()=>{
  const b=safeGet(dim,l);if(!b || b.typeId!==SNOW)return;
  const inventory=player.getComponent("minecraft:inventory")?.container,slot=player.selectedSlotIndex;
  const held=inventory?.getItem(slot);if(held?.typeId!=="minecraft:snow_layer")return;
  if(player.getGameMode()!==GameMode.Creative){if(held.amount<=1)inventory.setItem(slot,undefined);else{held.amount--;inventory.setItem(slot,held);}}
  const current=b.permutation.getState("classic_permafrost:layers");
  if(current<8)b.setPermutation(BlockPermutation.resolve(SNOW,{"classic_permafrost:layers":current+1}));
 });
});
world.afterEvents.playerBreakBlock.subscribe(event=>{
 const block=event.block,dim=block.dimension,l=block.location;
 if(event.brokenBlockPermutation.type.id===SNOW && event.player.getGameMode()!==GameMode.Creative){
  const tool=event.itemStackBeforeBreak;
  const silk=tool?.getComponent("minecraft:enchantable")?.getEnchantment("silk_touch");
  const layers=event.brokenBlockPermutation.getState("classic_permafrost:layers") ?? 1;
  const shovel=tool?.typeId?.endsWith("_shovel");
  if(silk || shovel)dim.spawnItem(new ItemStack(silk ? "minecraft:snow_layer" : "minecraft:snowball",silk ? 1 : layers),{x:l.x+.5,y:l.y+.5,z:l.z+.5});
 }
 const above=safeGet(dim,{x:l.x,y:l.y+1,z:l.z});
 // A protected snow layer loses its support when the block below is mined.
 if(above?.typeId===SNOW)above.setType("minecraft:air");
 if(event.brokenBlockPermutation.type.id===ICE && event.player.getGameMode()!==GameMode.Creative){
  const silk=event.itemStackBeforeBreak?.getComponent("minecraft:enchantable")?.getEnchantment("silk_touch");
  const below=safeGet(dim,{x:l.x,y:l.y-1,z:l.z});
  if(!silk && below?.isSolid && block.typeId==="minecraft:air")block.setType("minecraft:water");
 }
});
system.afterEvents.scriptEventReceive.subscribe(event=>{
 if(event.id==="classic_permafrost:revert"){
  reverting=true;scans.clear();world.sendMessage("Permafrost reversion enabled. Visit converted areas before removing the add-on; then exit the world.");
 }
});
system.runInterval(()=>{
 for(const player of world.getAllPlayers()){
  try{
   const dim=player.dimension,x=Math.floor(player.location.x),y=Math.floor(player.location.y),z=Math.floor(player.location.z);
   let state=scans.get(player.id);
   if(!state || state.d!==dim.id || Math.abs(state.x-x)>4 || Math.abs(state.z-z)>4){state={d:dim.id,x,z,index:0};scans.set(player.id,state);}
   for(let i=0;i<64;i++){
    const [dx,dz]=columns[state.index++ % columns.length],cx=state.x+dx,cz=state.z+dz;
    let top;try{top=dim.getTopmostBlock({x:cx,z:cz});}catch{}
    if(top)for(let dy=3;dy>=-12;dy--)convert(safeGet(dim,{x:cx,y:top.location.y+dy,z:cz}));
    for(let dy=-12;dy<=8;dy++)convert(safeGet(dim,{x:cx,y:y+dy,z:cz}));
   }
  }catch(error){console.warn(`[Permafrost] ${error}`);}
 }
},1);
