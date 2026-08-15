import asyncio
import sys
from pathlib import Path

# Insert backend directory
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.agents.ml_router import route_command, benchmark_latency
from app.tools.tool_registry import dispatch_tool

commands = [
    "open youtube and search yash songs",
    "search AI news on google",
    "open github",
    "open vscode",
    "open calculator",
    "send email to test@gmail.com",
]

async def main():
    print("=" * 65)
    print("  MJ AI ASSISTANT — LOCAL ML MODEL & TOOL DISPATCH VERIFICATION")
    print("=" * 65)
    
    for cmd in commands:
        routed = route_command(cmd)
        intent = routed["intent"]
        confidence = routed["confidence"]
        entities = routed["entities"]
        
        print(f"\n[Command] \"{cmd}\"")
        print(f"  -> Predicted Intent:  {intent} (Confidence: {confidence * 100:.2f}%)")
        print(f"  -> Extracted Entities: {entities}")
        
        # Tool execution test
        res = await dispatch_tool(intent, entities, raw_text=cmd)
        print(f"  -> Tool Action:       {res.get('action')}")
        print(f"  -> Execution Status:  {res.get('status')}")

    print("\n" + "=" * 65)
    print("  LATENCY BENCHMARK METRICS")
    print("=" * 65)
    bm = benchmark_latency()
    print(f"  -> Intent Classifier Latency: {bm['intent_latency_ms']} ms")
    print(f"  -> Entity Extractor Latency:  {bm['entity_latency_ms']} ms")
    print(f"  -> Total Local Routing Time:  {bm['total_latency_ms']} ms")
    print("=" * 65)

if __name__ == "__main__":
    asyncio.run(main())
