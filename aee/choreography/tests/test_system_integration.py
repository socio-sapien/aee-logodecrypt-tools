"""
System Integration Tests for AEE Choreography System

These tests verify that all components work together seamlessly
with absolute mathematical certainty and proper integration.
"""

import unittest
import json
import time
import os
import sys
from ..orchestration_engine import (
    ChoreographyEngine,
    get_choreography_engine,
    reset_choreography_engine,
    OrchestrationMode,
    InitiativeType,
    OptimizationStrategy
)

from ..aee_audit_inspector import (
    AEEAuditInspector,
    PreemptiveAuditSystem,
    AuditStatus,
    ComplianceLevel
)

from ..mathematical_certainty import (
    MathematicalCertaintyEngine,
    CertaintyLevel
)

from ..cross_platform_sync import (
    CrossPlatformSynchronizer,
    SyncStrategy,
    SyncStatus
)

from ..prime_integration import (
    PRIMEAuditIntegration,
    MCPToolIntegration,
    integrate_with_prime_system
)


class TestSystemIntegration(unittest.TestCase):
    """Test system integration"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Reset any existing engine
        reset_choreography_engine()
        
        # Create a fresh engine for each test
        self.engine = get_choreography_engine(
            name=f"test_engine_{time.time()}",
            mode=OrchestrationMode.ABSOLUTE,
            compliance_level=ComplianceLevel.ABSOLUTE,
            optimization_strategy=OptimizationStrategy.MATHEMATICAL
        )
    
    def tearDown(self):
        """Clean up after tests"""
        # Shutdown and reset the engine
        if self.engine:
            self.engine.shutdown()
        reset_choreography_engine()
    
    def test_engine_initialization(self):
        """Test that engine initializes correctly"""
        self.assertIsNotNone(self.engine)
        self.assertEqual(self.engine.mode, OrchestrationMode.ABSOLUTE)
        self.assertEqual(self.engine.compliance_level, ComplianceLevel.ABSOLUTE)
        self.assertTrue(self.engine.mathematical_absolute_certainty)
        self.assertTrue(self.engine.arithmetic_exactitude)
    
    def test_preemptive_audit_integration(self):
        """Test that preemptive audits are integrated correctly"""
        # Execute an initiative - should trigger preemptive audit
        result = self.engine.execute(
            initiative_type=InitiativeType.TASK,
            description="Test task for integration",
            data={"test": "integration"}
        )
        
        # The result should have an audit result
        self.assertIsNotNone(result.audit_result)
        self.assertEqual(result.audit_result.status, AuditStatus.PASSED)
        self.assertTrue(result.audit_result.verify())
    
    def test_mathematical_certainty_integration(self):
        """Test that mathematical certainty is maintained"""
        # Execute multiple initiatives
        results = []
        for i in range(3):
            result = self.engine.execute(
                initiative_type=InitiativeType.TASK,
                description=f"Test task {i}",
                data={"test": f"data_{i}"}
            )
            results.append(result)
        
        # All results should have mathematical certainty
        for result in results:
            self.assertTrue(result.verify())
            self.assertEqual(result.certainty_level, CertaintyLevel.ABSOLUTE)
    
    def test_workflow_execution(self):
        """Test workflow execution"""
        workflow_definition = {
            'name': 'test_workflow',
            'tasks': [
                {
                    'id': 'task_1',
                    'type': 'default',
                    'description': 'First test task',
                    'data': {'step': 1}
                },
                {
                    'id': 'task_2', 
                    'type': 'default',
                    'description': 'Second test task',
                    'data': {'step': 2}
                }
            ],
            'actions': [
                {
                    'id': 'action_1',
                    'type': 'default',
                    'description': 'Test action',
                    'data': {'action': 'test'}
                }
            ]
        }
        
        result = self.engine.execute_workflow(workflow_definition)
        
        self.assertEqual(result['status'], 'completed')
        self.assertIn('workflow_id', result)
        self.assertIn('results', result)
        self.assertTrue(result['certainty'] == 'absolute')
    
    def test_certainty_verification(self):
        """Test that certainty verification works"""
        # Execute some operations
        self.engine.execute(
            initiative_type=InitiativeType.TASK,
            description="Test certainty verification"
        )
        
        # Verify engine certainty
        certain = self.engine.verify_engine_certainty()
        self.assertTrue(certain)
    
    def test_agency_state_tracking(self):
        """Test that agency state is tracked correctly"""
        # Get initial state
        initial_state = self.engine.get_agency_state()
        self.assertEqual(initial_state.initiatives, [])
        self.assertEqual(initial_state.results, [])
        
        # Execute initiatives
        for i in range(3):
            self.engine.execute(
                initiative_type=InitiativeType.TASK,
                description=f"Tracked task {i}"
            )
        
        # Get updated state
        updated_state = self.engine.get_agency_state()
        self.assertEqual(len(updated_state.initiatives), 3)
        self.assertEqual(len(updated_state.results), 3)
    
    def test_optimization_report(self):
        """Test optimization report generation"""
        # Execute some operations
        for i in range(5):
            self.engine.execute(
                initiative_type=InitiativeType.TASK,
                description=f"Optimization test {i}"
            )
        
        # Get report
        report = self.engine.get_optimization_report()
        
        self.assertIn('engine_id', report)
        self.assertIn('engine_state', report)
        self.assertIn('automation_metrics', report)
        self.assertIn('audit_summary', report)
        self.assertTrue(report['mathematical_certainty'])
        self.assertTrue(report['arithmetic_exactitude'])


class TestPRIMEIntegration(unittest.TestCase):
    """Test PRIME integration"""
    
    def test_prime_audit_integration(self):
        """Test PRIME audit integration"""
        prime_integration = PRIMEAuditIntegration()
        
        # Test text audit
        result = prime_integration.audit_text("Test audit text")
        
        self.assertIn('prime_result', result)
        self.assertIn('mathematical_proof', result)
        self.assertIn('result_hash', result)
        self.assertTrue(result['certainty_level'] == 'absolute')
    
    def test_preemptive_prime_audit(self):
        """Test preemptive PRIME audit"""
        prime_integration = PRIMEAuditIntegration()
        
        audit_result = prime_integration.preemptive_prime_audit(
            "Test initiative",
            {"test": True}
        )
        
        self.assertIsNotNone(audit_result)
        self.assertTrue(audit_result.verify())
        self.assertTrue(audit_result.certainty_level == ComplianceLevel.ABSOLUTE)
    
    def test_prime_version(self):
        """Test PRIME version detection"""
        prime_integration = PRIMEAuditIntegration()
        version = prime_integration.get_prime_version()
        
        self.assertIsInstance(version, str)
        self.assertTrue(len(version) > 0)


class TestMCPIntegration(unittest.TestCase):
    """Test MCP tool integration"""
    
    def test_mcp_tool_registration(self):
        """Test MCP tool registration"""
        engine = get_choreography_engine(name="mcp_test")
        mcp_integration = MCPToolIntegration(engine)
        
        tools = mcp_integration.get_mcp_tools()
        
        self.assertIn('aee_execute', tools)
        self.assertIn('aee_audit', tools)
        self.assertIn('aee_verify', tools)
        self.assertIn('aee_status', tools)
        self.assertIn('aee_sync', tools)
    
    def test_mcp_tool_execution(self):
        """Test MCP tool execution"""
        engine = get_choreography_engine(name="mcp_execute_test")
        mcp_integration = MCPToolIntegration(engine)
        
        # Test aee_execute tool
        result = mcp_integration.call_tool('aee_execute', {
            'initiative_type': 'task',
            'description': 'Test MCP execution'
        })
        
        self.assertIn('status', result)
        self.assertEqual(result['status'], 'success')
        self.assertIn('result', result)
    
    def test_mcp_audit_tool(self):
        """Test MCP audit tool"""
        mcp_integration = MCPToolIntegration()
        
        result = mcp_integration.call_tool('aee_audit', {
            'description': 'Test audit via MCP',
            'audit_type': 'initiative'
        })
        
        self.assertIn('status', result)
        self.assertEqual(result['status'], 'success')
        self.assertIn('audit_result', result)


class TestCrossPlatformSyncIntegration(unittest.TestCase):
    """Test cross-platform synchronization integration"""
    
    def test_platform_registration(self):
        """Test platform registration"""
        sync = CrossPlatformSynchronizer()
        
        # Should have at least the current platform registered
        self.assertGreater(len(sync.platforms), 0)
    
    def test_synchronization(self):
        """Test synchronization execution"""
        sync = CrossPlatformSynchronizer()
        
        # Perform a synchronization
        sync_op = sync.synchronize_operation(
            operation_type="test",
            data={"test": "sync"},
            strategy=SyncStrategy.PARALLEL,
            preemptive_audit=True
        )
        
        self.assertEqual(sync_op.status, SyncStatus.COMPLETED)
        self.assertIsNotNone(sync_op.cryptographic_proof)
        self.assertTrue(sync_op.verify())


class TestComprehensiveSystem(unittest.TestCase):
    """Comprehensive system tests"""
    
    def test_full_system_workflow(self):
        """Test complete system workflow"""
        engine = get_choreography_engine(
            name="comprehensive_test",
            mode=OrchestrationMode.ABSOLUTE,
            compliance_level=ComplianceLevel.ABSOLUTE
        )
        
        try:
            # 1. Create and execute initiatives
            for i in range(5):
                result = engine.execute(
                    initiative_type=InitiativeType.TASK,
                    description=f"Comprehensive test task {i}",
                    data={"test": f"data_{i}", "iteration": i}
                )
                self.assertEqual(result.status, 'completed')
                self.assertTrue(result.verify())
            
            # 2. Execute a workflow
            workflow = {
                'name': 'comprehensive_workflow',
                'tasks': [
                    {'id': 'wf_task_1', 'type': 'default', 'description': 'Workflow task 1'},
                    {'id': 'wf_task_2', 'type': 'default', 'description': 'Workflow task 2'}
                ]
            }
            workflow_result = engine.execute_workflow(workflow)
            self.assertEqual(workflow_result['status'], 'completed')
            
            # 3. Verify engine certainty
            self.assertTrue(engine.verify_engine_certainty())
            
            # 4. Get optimization report
            report = engine.get_optimization_report()
            self.assertIn('automation_metrics', report)
            self.assertIn('audit_summary', report)
            
            # 5. Check cumulative audit
            audit_summary = engine.get_cumulative_audit_summary()
            self.assertGreater(audit_summary['total_audits'], 0)
            self.assertEqual(audit_summary['passed_audits'], audit_summary['total_audits'])
            
            return True
            
        finally:
            engine.shutdown()
            reset_choreography_engine()
    
    def test_mathematical_absolute_certainty(self):
        """Test that mathematical absolute certainty is maintained throughout"""
        engine = get_choreography_engine(
            name="certainty_test",
            mode=OrchestrationMode.ABSOLUTE
        )
        
        try:
            # Execute various operations
            operations = [
                (InitiativeType.TASK, "Task with certainty"),
                (InitiativeType.ACTION, "Action with certainty"),
                (InitiativeType.WORKFLOW, "Workflow with certainty"),
                (InitiativeType.OPERATION, "Operation with certainty")
            ]
            
            for init_type, description in operations:
                result = engine.execute(init_type, description)
                
                # Each result must have absolute certainty
                self.assertEqual(result.certainty_level, CertaintyLevel.ABSOLUTE)
                self.assertTrue(result.verify())
                
                # The audit must have passed
                self.assertIsNotNone(result.audit_result)
                self.assertEqual(result.audit_result.status, AuditStatus.PASSED)
            
            # Final verification
            self.assertTrue(engine.verify_engine_certainty())
            self.assertTrue(engine.mathematical_absolute_certainty)
            self.assertTrue(engine.arithmetic_exactitude)
            
            return True
            
        finally:
            engine.shutdown()
            reset_choreography_engine()
    
    def test_preemptive_audit_requirements(self):
        """Test that preemptive audits are performed before every operation"""
        engine = get_choreography_engine(
            name="audit_requirement_test",
            compliance_level=ComplianceLevel.ABSOLUTE
        )
        
        try:
            # The audit system should track all audits
            initial_audits = engine.audit_system.audit_inspector.cumulative_record.total_audits
            
            # Execute an initiative
            engine.execute(
                initiative_type=InitiativeType.TASK,
                description="Audit requirement test"
            )
            
            # Should have one more audit
            updated_audits = engine.audit_system.audit_inspector.cumulative_record.total_audits
            self.assertEqual(updated_audits, initial_audits + 1)
            
            # Execute a workflow
            workflow = {'name': 'audit_test', 'tasks': [{'id': '1', 'type': 'default', 'description': 'test'}]}
            engine.execute_workflow(workflow)
            
            # Should have more audits
            final_audits = engine.audit_system.audit_inspector.cumulative_record.total_audits
            self.assertGreater(final_audits, updated_audits)
            
            # All audits should be verifiable
            self.assertTrue(engine.audit_system.audit_inspector.verify_all_audits())
            
            return True
            
        finally:
            engine.shutdown()
            reset_choreography_engine()


if __name__ == '__main__':
    unittest.main()
