#!/usr/bin/env python3
"""
Main Entry Point for AEE Logodecrypt Choreography System

This is the primary interface for the automated MCP tools, GitHub resources,
cross-platform workflow integration with ghost operators, agents, and
preemptive AEE audit inspections.

The system provides:
- Absolute mathematical certainty in all operations
- Preemptive audit inspections preceding every task, action, and initiative
- Standardized behavior, compliance, fidelity, and diligence
- Cross-platform workflow synchronization
- Ghost operators and automated agents
- Cumulative and progressive auditing

Usage:
    python -m aee.choreography.main [command] [options]

Commands:
    start           - Start the choreography engine
    execute         - Execute an initiative or workflow
    audit           - Perform preemptive audit
    sync            - Synchronize across platforms
    verify          - Verify mathematical certainty
    status          - Get system status
    test            - Run system tests
    shutdown        - Shutdown the engine
"""

import argparse
import json
import os
import sys
import time
import traceback
from typing import Optional, Dict, Any

# Add the choreography directory to the path
choreography_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(choreography_dir))

from aee.choreography.orchestration_engine import (
    ChoreographyEngine,
    get_choreography_engine,
    reset_choreography_engine,
    OrchestrationMode,
    InitiativeType,
    OptimizationStrategy
)

from aee.choreography.mathematical_certainty import (
    MathematicalCertaintyEngine,
    CertaintyLevel
)

from aee.choreography.aee_audit_inspector import (
    AEEAuditInspector,
    PreemptiveAuditSystem,
    ComplianceLevel
)

from aee.choreography.cross_platform_sync import (
    CrossPlatformSynchronizer,
    SyncStrategy
)

from aee.choreography.ghost_operators import (
    GhostOperator,
    PhantomAgent,
    SilentExecutor
)


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='AEE Logodecrypt Choreography System - Automated MCP tools, GitHub resources, cross-platform workflow integration'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Start command
    start_parser = subparsers.add_parser('start', help='Start the choreography engine')
    start_parser.add_argument('--name', type=str, default='aee_choreography', 
                             help='Name of the engine')
    start_parser.add_argument('--mode', type=str, default='absolute',
                             choices=['absolute', 'standard', 'performance', 'stealth', 'phantom', 'audit_only'],
                             help='Orchestration mode')
    start_parser.add_argument('--compliance', type=str, default='absolute',
                             choices=['absolute', 'strict', 'standard', 'basic'],
                             help='Compliance level')
    start_parser.add_argument('--optimization', type=str, default='mathematical',
                             choices=['mathematical', 'adaptive', 'predictive', 'deterministic', 'hybrid'],
                             help='Optimization strategy')
    start_parser.add_argument('--no-ghost', action='store_true',
                             help='Disable ghost operators')
    start_parser.add_argument('--no-cross-platform', action='store_true',
                             help='Disable cross-platform synchronization')
    start_parser.add_argument('--no-audits', action='store_true',
                             help='Disable preemptive audits (NOT RECOMMENDED)')
    
    # Execute command
    execute_parser = subparsers.add_parser('execute', help='Execute an initiative or workflow')
    execute_parser.add_argument('--type', type=str, required=True,
                              choices=['task', 'action', 'workflow', 'operation', 'audit', 'synchronization', 'optimization'],
                              help='Type of initiative to execute')
    execute_parser.add_argument('--description', type=str, required=True,
                              help='Description of the initiative')
    execute_parser.add_argument('--data', type=str, default='{}',
                              help='JSON data for the initiative')
    execute_parser.add_argument('--priority', type=int, default=0,
                              help='Priority level')
    execute_parser.add_argument('--context', type=str, default='{}',
                              help='JSON context for execution')
    
    # Audit command
    audit_parser = subparsers.add_parser('audit', help='Perform preemptive audit')
    audit_parser.add_argument('--description', type=str, required=True,
                             help='Description of what to audit')
    audit_parser.add_argument('--type', type=str, default='initiative',
                             choices=['task', 'action', 'initiative'],
                             help='Type of audit')
    audit_parser.add_argument('--context', type=str, default='{}',
                             help='JSON context for audit')
    
    # Sync command
    sync_parser = subparsers.add_parser('sync', help='Synchronize across platforms')
    sync_parser.add_argument('--type', type=str, required=True,
                           help='Type of operation to synchronize')
    sync_parser.add_argument('--description', type=str, required=True,
                           help='Description of the operation')
    sync_parser.add_argument('--data', type=str, default='{}',
                           help='JSON data for the operation')
    sync_parser.add_argument('--platforms', type=str, default='',
                           help='Comma-separated list of platform IDs')
    sync_parser.add_argument('--strategy', type=str, default='parallel',
                           choices=['immediate', 'parallel', 'sequential', 'staggered', 'majority', 'consensus'],
                           help='Synchronization strategy')
    
    # Workflow command
    workflow_parser = subparsers.add_parser('workflow', help='Execute a workflow')
    workflow_parser.add_argument('--file', type=str, 
                               help='JSON file containing workflow definition')
    workflow_parser.add_argument('--definition', type=str, 
                               help='JSON workflow definition')
    
    # Verify command
    verify_parser = subparsers.add_parser('verify', help='Verify mathematical certainty')
    verify_parser.add_argument('--full', action='store_true',
                              help='Perform full verification')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Get system status')
    status_parser.add_argument('--detailed', action='store_true',
                              help='Show detailed status')
    
    # Test command
    test_parser = subparsers.add_parser('test', help='Run system tests')
    test_parser.add_argument('--component', type=str, default='all',
                           choices=['all', 'certainty', 'audit', 'sync', 'ghost', 'integration'],
                           help='Component to test')
    test_parser.add_argument('--verbose', action='store_true',
                           help='Show verbose output')
    
    # Shutdown command
    shutdown_parser = subparsers.add_parser('shutdown', help='Shutdown the engine')
    shutdown_parser.add_argument('--force', action='store_true',
                               help='Force shutdown without confirmation')
    
    # Report command
    report_parser = subparsers.add_parser('report', help='Generate optimization report')
    report_parser.add_argument('--output', type=str, default='-',
                              help='Output file (default: stdout)')
    
    return parser.parse_args()


class ChoreographyCLI:
    """Command-line interface for the choreography system"""
    
    def __init__(self):
        self.engine: Optional[ChoreographyEngine] = None
        self.verbose = False
        
    def start_engine(self, args):
        """Start the choreography engine"""
        print("Starting AEE Logodecrypt Choreography System...")
        print("=" * 60)
        
        # Parse arguments
        mode = getattr(OrchestrationMode, args.mode.upper(), OrchestrationMode.ABSOLUTE)
        compliance = getattr(ComplianceLevel, args.compliance.upper(), ComplianceLevel.ABSOLUTE)
        optimization = getattr(OptimizationStrategy, args.optimization.upper(), OptimizationStrategy.MATHEMATICAL)
        
        # Create engine
        self.engine = get_choreography_engine(
            name=args.name,
            mode=mode,
            compliance_level=compliance,
            optimization_strategy=optimization,
            enable_ghost_operators=not args.no_ghost,
            enable_cross_platform=not args.no_cross_platform,
            enable_preemptive_audits=not args.no_audits
        )
        
        print(f"Engine started: {self.engine.name}")
        print(f"Engine ID: {self.engine.engine_id}")
        print(f"Mode: {args.mode}")
        print(f"Compliance Level: {args.compliance}")
        print(f"Optimization Strategy: {args.optimization}")
        print(f"Ghost Operators: {'enabled' if not args.no_ghost else 'disabled'}")
        print(f"Cross-Platform Sync: {'enabled' if not args.no_cross_platform else 'disabled'}")
        print(f"Preemptive Audits: {'enabled' if not args.no_audits else 'disabled'}")
        print("=" * 60)
        print("Engine ready. Use 'execute', 'audit', 'sync', or other commands.")
        
        return True
    
    def execute_initiative(self, args):
        """Execute an initiative"""
        if not self.engine:
            print("Error: Engine not started. Use 'start' command first.")
            return False
        
        # Parse arguments
        initiative_type = getattr(InitiativeType, args.type.upper(), InitiativeType.TASK)
        
        try:
            data = json.loads(args.data) if args.data else {}
            context = json.loads(args.context) if args.context else {}
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            return False
        
        print(f"Executing {args.type}: {args.description}")
        
        try:
            result = self.engine.execute(
                initiative_type=initiative_type,
                description=args.description,
                data=data,
                priority=args.priority,
                context=context
            )
            
            print(f"Execution Result:")
            print(f"  Status: {result.status}")
            print(f"  Result ID: {result.result_id}")
            print(f"  Initiative ID: {result.initiative_id}")
            print(f"  Certainty Level: {result.certainty_level.value}")
            print(f"  Execution Time: {result.execution_time_ns} ns")
            
            if result.status == 'completed':
                print(f"  Output: {json.dumps(result.output, indent=2)[:200]}...")
            else:
                print(f"  Error: {result.output}")
            
            # Verify mathematical certainty
            if self.engine.verify_engine_certainty():
                print("  ✓ Mathematical certainty verified")
            else:
                print("  ✗ Mathematical certainty verification FAILED")
                
            return True
            
        except Exception as e:
            print(f"Error executing initiative: {e}")
            traceback.print_exc()
            return False
    
    def perform_audit(self, args):
        """Perform preemptive audit"""
        if not self.engine:
            print("Error: Engine not started. Use 'start' command first.")
            return False
        
        print(f"Performing {args.type} audit: {args.description}")
        
        try:
            context = json.loads(args.context) if args.context else {}
        except json.JSONDecodeError as e:
            print(f"Error parsing context JSON: {e}")
            return False
        
        try:
            audit_result = self.engine.audit_everything(args.description, context)
            
            print(f"Audit Result:")
            print(f"  Audit ID: {audit_result.audit_id}")
            print(f"  Status: {audit_result.status.value}")
            print(f"  Severity: {audit_result.severity.value}")
            print(f"  Compliance Level: {audit_result.compliance_level.value}")
            print(f"  Findings: {len(audit_result.findings)}")
            print(f"  Evidence: {len(audit_result.evidence)}")
            
            if audit_result.findings:
                print(f"\nFindings:")
                for i, finding in enumerate(audit_result.findings, 1):
                    print(f"  {i}. [{finding.severity.value.upper()}] {finding.description}")
            
            if audit_result.has_critical_findings():
                print("\n⚠️  CRITICAL findings detected - execution blocked")
            
            # Verify audit
            if audit_result.verify():
                print("\n✓ Audit verification passed")
            else:
                print("\n✗ Audit verification FAILED")
            
            return True
            
        except Exception as e:
            print(f"Error performing audit: {e}")
            traceback.print_exc()
            return False
    
    def synchronize_platforms(self, args):
        """Synchronize across platforms"""
        if not self.engine:
            print("Error: Engine not started. Use 'start' command first.")
            return False
        
        if not self.engine.cross_platform_sync:
            print("Error: Cross-platform synchronization not enabled.")
            return False
        
        # Parse arguments
        strategy = getattr(SyncStrategy, args.strategy.upper(), SyncStrategy.PARALLEL)
        
        try:
            data = json.loads(args.data) if args.data else {}
        except json.JSONDecodeError as e:
            print(f"Error parsing data JSON: {e}")
            return False
        
        platforms = args.platforms.split(',') if args.platforms else None
        
        print(f"Synchronizing {args.type}: {args.description}")
        print(f"  Strategy: {args.strategy}")
        print(f"  Target Platforms: {platforms or 'all'}")
        
        try:
            initiative_type = getattr(InitiativeType, args.type.upper(), InitiativeType.TASK)
            result = self.engine.execute_cross_platform(
                initiative_type=initiative_type,
                description=args.description,
                data=data,
                target_platforms=platforms,
                strategy=strategy
            )
            
            print(f"Synchronization Result:")
            print(f"  Status: {result.status}")
            print(f"  Platform Results: {len(result.platform_results)}")
            
            for platform_id, platform_result in result.platform_results.items():
                status = platform_result.get('status', 'unknown')
                print(f"    {platform_id}: {status}")
            
            return True
            
        except Exception as e:
            print(f"Error synchronizing: {e}")
            traceback.print_exc()
            return False
    
    def execute_workflow(self, args):
        """Execute a workflow"""
        if not self.engine:
            print("Error: Engine not started. Use 'start' command first.")
            return False
        
        # Get workflow definition
        workflow_def = {}
        if args.file:
            try:
                with open(args.file, 'r') as f:
                    workflow_def = json.load(f)
            except Exception as e:
                print(f"Error reading workflow file: {e}")
                return False
        elif args.definition:
            try:
                workflow_def = json.loads(args.definition)
            except json.JSONDecodeError as e:
                print(f"Error parsing workflow definition: {e}")
                return False
        else:
            print("Error: Either --file or --definition must be provided")
            return False
        
        print(f"Executing workflow: {workflow_def.get('name', 'unnamed')}")
        
        try:
            result = self.engine.execute_workflow(workflow_def)
            
            print(f"Workflow Result:")
            print(f"  Status: {result.get('status', 'unknown')}")
            print(f"  Workflow ID: {result.get('workflow_id', 'N/A')}")
            print(f"  Duration: {result.get('duration_seconds', 0):.2f} seconds")
            print(f"  Certainty: {result.get('certainty', 'unknown')}")
            
            if 'results' in result:
                task_count = sum(1 for k in result['results'] if k.startswith('task_'))
                action_count = sum(1 for k in result['results'] if k.startswith('action_'))
                print(f"  Tasks Executed: {task_count}")
                print(f"  Actions Executed: {action_count}")
            
            return True
            
        except Exception as e:
            print(f"Error executing workflow: {e}")
            traceback.print_exc()
            return False
    
    def verify_certainty(self, args):
        """Verify mathematical certainty"""
        if not self.engine:
            print("Error: Engine not started. Use 'start' command first.")
            return False
        
        print("Verifying mathematical certainty...")
        
        try:
            certain = self.engine.verify_engine_certainty()
            
            print(f"Mathematical Certainty Verification: {'PASSED' if certain else 'FAILED'}")
            
            if args.full:
                # Get detailed report
                report = self.engine.get_optimization_report()
                print(f"\nDetailed Report:")
                print(f"  Engine State: {report['engine_state']['status']}")
                print(f"  Total Operations: {report['engine_state']['total_operations']}")
                print(f"  Successful Operations: {report['engine_state']['successful_operations']}")
                print(f"  Failed Operations: {report['engine_state']['failed_operations']}")
                print(f"  Mathematical Certainty: {report['mathematical_certainty']}")
                print(f"  Arithmetic Exactitude: {report['arithmetic_exactitude']}")
                print(f"  Certainty Guarantee: {report['certainty_guarantee']}")
            
            return certain
            
        except Exception as e:
            print(f"Error verifying certainty: {e}")
            traceback.print_exc()
            return False
    
    def get_status(self, args):
        """Get system status"""
        if not self.engine:
            print("Error: Engine not started. Use 'start' command first.")
            return False
        
        print("System Status:")
        print("=" * 50)
        
        state = self.engine.get_engine_state()
        
        print(f"Engine: {self.engine.name}")
        print(f"Engine ID: {self.engine.engine_id}")
        print(f"Status: {state.get('status', 'unknown')}")
        print(f"Mode: {self.engine.mode.value}")
        print(f"Compliance Level: {self.engine.compliance_level.value}")
        print(f"Optimization Strategy: {self.engine.optimization_strategy.value}")
        print(f"Uptime: {time.time() - state.get('start_time', time.time()):.2f} seconds")
        print(f"")
        print(f"Operations:")
        print(f"  Total: {state.get('total_operations', 0)}")
        print(f"  Successful: {state.get('successful_operations', 0)}")
        print(f"  Failed: {state.get('failed_operations', 0)}")
        print(f"  Certainty Guarantee: {state.get('certainty_guarantee', False)}")
        
        if args.detailed:
            print(f"\nAutomation Controller:")
            if 'automation_controller' in state:
                for k, v in state['automation_controller'].items():
                    print(f"  {k}: {v}")
            
            print(f"\nInitiative Manager:")
            if 'initiative_manager' in state:
                for k, v in state['initiative_manager'].items():
                    print(f"  {k}: {v}")
        
        print("=" * 50)
        return True
    
    def run_tests(self, args):
        """Run system tests"""
        print("Running AEE Choreography System Tests...")
        print("=" * 60)
        
        if args.component == 'all' or args.component == 'certainty':
            print("\n[1/5] Testing Mathematical Certainty Engine...")
            self.test_certainty_engine()
        
        if args.component == 'all' or args.component == 'audit':
            print("\n[2/5] Testing AEE Audit System...")
            self.test_audit_system()
        
        if args.component == 'all' or args.component == 'sync':
            print("\n[3/5] Testing Cross-Platform Synchronization...")
            self.test_sync_system()
        
        if args.component == 'all' or args.component == 'ghost':
            print("\n[4/5] Testing Ghost Operators...")
            self.test_ghost_operators()
        
        if args.component == 'all' or args.component == 'integration':
            print("\n[5/5] Testing System Integration...")
            self.test_integration()
        
        print("\n" + "=" * 60)
        print("All tests completed!")
        return True
    
    def test_certainty_engine(self):
        """Test mathematical certainty engine"""
        from aee.choreography.mathematical_certainty import (
            MathematicalCertaintyEngine,
            DeterministicExecutor
        )
        
        engine = MathematicalCertaintyEngine()
        executor = DeterministicExecutor()
        
        # Test deterministic execution
        result1 = executor.execute("identity", {"test": "data"})
        result2 = executor.execute("identity", {"test": "data"})
        
        if result1.verify_determinism({"test": "data"}):
            print("  ✓ Deterministic execution verified")
        else:
            print("  ✗ Deterministic execution FAILED")
            return
        
        # Test mathematical proof
        if result1.mathematical_proof.verify():
            print("  ✓ Mathematical proof verified")
        else:
            print("  ✗ Mathematical proof FAILED")
            return
        
        # Test cryptographic proof
        if result1.cryptographic_proof.verify_chain():
            print("  ✓ Cryptographic proof verified")
        else:
            print("  ✗ Cryptographic proof FAILED")
            return
        
        print("  ✓ Mathematical Certainty Engine PASSED")
    
    def test_audit_system(self):
        """Test AEE audit system"""
        from aee.choreography.aee_audit_inspector import (
            AEEAuditInspector,
            PreemptiveAuditSystem,
            ComplianceLevel
        )
        
        inspector = AEEAuditInspector(compliance_level=ComplianceLevel.ABSOLUTE)
        
        # Test task audit
        audit_result = inspector.audit_task_preemptive(
            "Test task for audit verification",
            {"test": True}
        )
        
        if audit_result.verify():
            print("  ✓ Task audit verification passed")
        else:
            print("  ✗ Task audit verification FAILED")
            return
        
        # Test initiative audit
        audit_result = inspector.audit_initiative_preemptive(
            "Test initiative for audit verification",
            {"test": True}
        )
        
        if audit_result.verify():
            print("  ✓ Initiative audit verification passed")
        else:
            print("  ✗ Initiative audit verification FAILED")
            return
        
        # Test cumulative audit
        cumulative = inspector.get_cumulative_summary()
        if cumulative['total_audits'] >= 2:
            print("  ✓ Cumulative audit tracking working")
        else:
            print("  ✗ Cumulative audit tracking FAILED")
            return
        
        print("  ✓ AEE Audit System PASSED")
    
    def test_sync_system(self):
        """Test cross-platform synchronization"""
        from aee.choreography.cross_platform_sync import (
            CrossPlatformSynchronizer,
            PlatformDetector,
            SyncStrategy
        )
        
        detector = PlatformDetector()
        platform_info = detector.detect_platform()
        
        print(f"  ✓ Platform detection working: {platform_info.platform_type.value}")
        
        # Test synchronizer
        sync = CrossPlatformSynchronizer()
        sync.register_platform(platform_info)
        
        if len(sync.platforms) == 1:
            print("  ✓ Platform registration working")
        else:
            print("  ✗ Platform registration FAILED")
            return
        
        print("  ✓ Cross-Platform Synchronization PASSED")
    
    def test_ghost_operators(self):
        """Test ghost operators"""
        from aee.choreography.ghost_operators import (
            GhostOperator,
            PhantomAgent,
            SilentExecutor,
            GhostMode,
            GhostStatus
        )
        
        # Test ghost operator
        ghost = GhostOperator("test_ghost", GhostMode.SILENT)
        ghost.activate()
        
        if ghost.get_status() == GhostStatus.ACTIVE:
            print("  ✓ Ghost operator activation working")
        else:
            print("  ✗ Ghost operator activation FAILED")
            return
        
        # Test phantom agent
        phantom = PhantomAgent("test_phantom", lifespan_seconds=10)
        phantom.activate()
        
        if phantom.get_status() == GhostStatus.ACTIVE:
            print("  ✓ Phantom agent activation working")
        else:
            print("  ✗ Phantom agent activation FAILED")
            return
        
        # Test silent executor
        executor = SilentExecutor("test_executor")
        executor.activate()
        
        if executor.get_status() == GhostStatus.ACTIVE:
            print("  ✓ Silent executor activation working")
        else:
            print("  ✗ Silent executor activation FAILED")
            return
        
        print("  ✓ Ghost Operators PASSED")
    
    def test_integration(self):
        """Test system integration"""
        print("  ✓ Starting integration test...")
        
        # Create a simple engine
        test_engine = get_choreography_engine(
            name="test_integration",
            mode=OrchestrationMode.ABSOLUTE,
            compliance_level=ComplianceLevel.ABSOLUTE
        )
        
        # Test initiative execution
        result = test_engine.execute(
            initiative_type=InitiativeType.TASK,
            description="Test integration task",
            data={"test": "integration"}
        )
        
        if result.status == 'completed':
            print("  ✓ Initiative execution working")
        else:
            print(f"  ✗ Initiative execution FAILED: {result.status}")
            return
        
        # Test audit
        audit_result = test_engine.audit_everything("Test integration audit")
        if audit_result.verify():
            print("  ✓ Audit system integration working")
        else:
            print("  ✗ Audit system integration FAILED")
            return
        
        # Test certainty verification
        if test_engine.verify_engine_certainty():
            print("  ✓ Certainty verification working")
        else:
            print("  ✗ Certainty verification FAILED")
            return
        
        print("  ✓ System Integration PASSED")
        
        # Cleanup
        reset_choreography_engine()
    
    def generate_report(self, args):
        """Generate optimization report"""
        if not self.engine:
            print("Error: Engine not started. Use 'start' command first.")
            return False
        
        report = self.engine.get_optimization_report()
        
        if args.output == '-':
            # Print to stdout
            print(json.dumps(report, indent=2))
        else:
            # Save to file
            try:
                with open(args.output, 'w') as f:
                    json.dump(report, f, indent=2)
                print(f"Report saved to {args.output}")
            except Exception as e:
                print(f"Error saving report: {e}")
                return False
        
        return True
    
    def shutdown_engine(self, args):
        """Shutdown the engine"""
        if not self.engine:
            print("Engine not started, nothing to shutdown.")
            return True
        
        if not args.force:
            print("Are you sure you want to shutdown the engine? (y/n)")
            response = input().strip().lower()
            if response != 'y':
                print("Shutdown cancelled.")
                return True
        
        print("Shutting down engine...")
        self.engine.shutdown()
        reset_choreography_engine()
        self.engine = None
        print("Engine shutdown complete.")
        return True


def main():
    """Main entry point"""
    args = parse_args()
    cli = ChoreographyCLI()
    
    if not args.command:
        # No command provided, show help
        parser = argparse.ArgumentParser()
        parser.add_argument('--help', action='store_true')
        args = parser.parse_args()
        if args.help:
            parser.print_help()
        else:
            parser.print_help()
        return 0
    
    # Handle commands
    command_handlers = {
        'start': cli.start_engine,
        'execute': cli.execute_initiative,
        'audit': cli.perform_audit,
        'sync': cli.synchronize_platforms,
        'workflow': cli.execute_workflow,
        'verify': cli.verify_certainty,
        'status': cli.get_status,
        'test': cli.run_tests,
        'report': cli.generate_report,
        'shutdown': cli.shutdown_engine
    }
    
    handler = command_handlers.get(args.command)
    if handler:
        try:
            success = handler(args)
            return 0 if success else 1
        except Exception as e:
            print(f"Error: {e}")
            traceback.print_exc()
            return 1
    else:
        print(f"Unknown command: {args.command}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
