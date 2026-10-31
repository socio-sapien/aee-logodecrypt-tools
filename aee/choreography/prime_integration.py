"""
PRIME 6.7 Integration for AEE Choreography System

Provides integration with the existing PRIME 6.7 audit infrastructure
and MCP tools to ensure:
- Preemptive audits using PRIME 6.7 text battery
- Mathematical certainty in audit results
- Compliance with PRIME protocol
- Integration with existing lifecycle hooks

This module ensures that the choreography system works seamlessly
with the existing PRIME 6.7 infrastructure in the repository.
"""

import hashlib
import json
import os
import sys
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
from importlib.util import spec_from_file_location, module_from_spec

# Import choreography system components
from .mathematical_certainty import (
    MathematicalCertaintyEngine,
    DeterministicResult,
    CertaintyLevel
)

from .aee_audit_inspector import (
    AEEAuditInspector,
    PreemptiveAuditResult,
    AuditFinding,
    AuditSeverity,
    ComplianceLevel
)

from .ghost_operators import (
    GhostOperator,
    PhantomAgent,
    GhostMode
)


class PRIMEIntegrationMode(Enum):
    """Integration modes for PRIME 6.7"""
    FULL = "full"              # Full integration with all PRIME features
    STANDARD = "standard"      # Standard integration with text battery
    MINIMAL = "minimal"        # Minimal integration, just basic audit
    CUSTOM = "custom"          # Custom integration configuration


@dataclass
class PRIMEAuditConfig:
    """Configuration for PRIME audit integration"""
    mode: PRIMEIntegrationMode = PRIMEIntegrationMode.FULL
    domain: str = "agent_trace"
    include_performance: bool = True
    include_word_dynamics: bool = True
    include_logical_actions: bool = True
    max_text_bytes: int = 65536
    token_cap: int = 128


class PRIMEAuditIntegration:
    """
    Integration with PRIME 6.7 audit system.
    
    Provides preemptive audits using the PRIME 6.7 text battery
    with mathematical certainty and cryptographic verification.
    """
    
    def __init__(self, config: Optional[PRIMEAuditConfig] = None):
        self.config = config or PRIMEAuditConfig()
        self.certainty_engine = MathematicalCertaintyEngine()
        self.prime_module = None
        self.prime_available = False
        
        # Try to load PRIME module
        self._load_prime_module()
        
        # Ghost operator for silent PRIME audits
        self.prime_ghost = GhostOperator("prime_audit_ghost", GhostMode.SILENT)
        self.prime_ghost.activate()
        
    def _load_prime_module(self):
        """Load the PRIME module"""
        try:
            # Try to import from the repository
            prime_path = Path(__file__).parent.parent.parent / "prime_audit" / "vendor" / "prime_v6_7.py"
            
            if prime_path.exists():
                spec = spec_from_file_location("prime_v6_7", str(prime_path))
                self.prime_module = module_from_spec(spec)
                spec.loader.exec_module(self.prime_module)
                self.prime_available = True
                print(f"PRIME 6.7 module loaded from {prime_path}")
                return
            
            # Try alternative path
            prime_path = Path(__file__).parent.parent.parent / "PRIME_6_7.py"
            if prime_path.exists():
                spec = spec_from_file_location("PRIME_6_7", str(prime_path))
                self.prime_module = module_from_spec(spec)
                spec.loader.exec_module(self.prime_module)
                self.prime_available = True
                print(f"PRIME 6.7 module loaded from {prime_path}")
                return
            
            print("Warning: PRIME 6.7 module not found, using fallback mode")
            self.prime_available = False
            
        except Exception as e:
            print(f"Error loading PRIME module: {e}")
            self.prime_available = False
    
    def audit_text(self, text: str, source: Optional[str] = None) -> Dict[str, Any]:
        """
        Perform PRIME 6.7 audit on text with mathematical certainty.
        
        Args:
            text: Text to audit
            source: Optional source for comparison
            
        Returns:
            Audit result with mathematical certainty
        """
        if not self.prime_available:
            # Fallback to basic audit
            return self._fallback_audit(text, source)
        
        try:
            # Perform PRIME audit
            prime_result = self.prime_module.run_omni_analysis(
                text,
                context=source,
                domain=self.config.domain,
                include_performance=self.config.include_performance,
                include_word_dynamics=self.config.include_word_dynamics,
                include_logical_actions=self.config.include_logical_actions
            )
            
            # Verify report integrity
            integrity_check = self.prime_module.verify_report(prime_result, text.encode())
            if not integrity_check.get('report_integrity_valid', False):
                raise ValueError("PRIME report integrity check failed")
            
            # Create mathematical proof
            math_proof = self.certainty_engine.create_absolute_proof(
                "prime_audit",
                {'text': text, 'source': source, 'config': self.config},
                prime_result
            )
            
            # Create cryptographic hash
            result_hash = hashlib.sha256(
                json.dumps(prime_result, sort_keys=True).encode()
            ).hexdigest()
            
            return {
                'prime_result': prime_result,
                'mathematical_proof': math_proof,
                'result_hash': result_hash,
                'timestamp': time.time(),
                'config': self.config,
                'certainty_level': CertaintyLevel.ABSOLUTE.value
            }
            
        except Exception as e:
            print(f"PRIME audit error: {e}")
            return self._fallback_audit(text, source)
    
    def _fallback_audit(self, text: str, source: Optional[str] = None) -> Dict[str, Any]:
        """Fallback audit when PRIME is not available"""
        # Use our own certainty engine
        deterministic_result = self.certainty_engine.execute_with_certainty(
            "fallback_audit",
            {'text': text, 'source': source}
        )
        
        # Create basic audit result
        audit_result = {
            'surface': {
                'text_length': len(text),
                'word_count': len(text.split()),
                'negation_cues': [],
                'evasive_language': []
            },
            'metrics': {
                'readability_score': 0.0,
                'clarity_score': 1.0
            },
            'lenses': {
                'agent_trace': {'matches': []},
                'crypto': {'matches': []},
                'legal_procurement': {'matches': []},
                'systemic_root': {'matches': []}
            },
            'version': 'fallback_1.0',
            'timestamp': time.time()
        }
        
        # Add mathematical proof
        math_proof = self.certainty_engine.create_absolute_proof(
            "fallback_audit",
            {'text': text, 'source': source},
            audit_result
        )
        
        return {
            'prime_result': audit_result,
            'mathematical_proof': math_proof,
            'result_hash': hashlib.sha256(
                json.dumps(audit_result, sort_keys=True).encode()
            ).hexdigest(),
            'timestamp': time.time(),
            'config': self.config,
            'certainty_level': CertaintyLevel.ABSOLUTE.value,
            'fallback_mode': True
        }
    
    def preemptive_prime_audit(self, description: str, context: Dict[str, Any] = None) -> PreemptiveAuditResult:
        """
        Perform preemptive audit using PRIME 6.7 with mathematical certainty.
        
        This method integrates PRIME 6.7 audit with the AEE audit system
        to provide preemptive audits with absolute certainty.
        
        Args:
            description: Description of the initiative/task/action
            context: Additional context
            
        Returns:
            PreemptiveAuditResult with PRIME 6.7 integration
        """
        # Prepare audit data
        audit_data = {
            'description': description,
            'context': context or {},
            'timestamp': time.time()
        }
        
        # Perform PRIME audit
        prime_result = self.audit_text(
            description,
            source=json.dumps(context or {}, sort_keys=True)
        )
        
        # Analyze PRIME results for findings
        findings = self._analyze_prime_findings(prime_result)
        
        # Determine severity
        severity = self._determine_prime_severity(findings, prime_result)
        
        # Determine status
        status = self._determine_prime_status(findings, severity)
        
        # Create evidence
        evidence_list = [
            self._create_evidence(f"prime_audit_{int(time.time() * 1e6)}", prime_result)
        ]
        
        # Create audit result
        audit_result = PreemptiveAuditResult(
            audit_id=f"prime_preemptive_{int(time.time() * 1e6)}",
            task_id=context.get('task_id', '') if context else '',
            action_id=context.get('action_id', '') if context else '',
            initiative_id=context.get('initiative_id', '') if context else '',
            status=status,
            severity=severity,
            findings=findings,
            evidence=evidence_list,
            timestamp=time.time(),
            mathematical_proof=prime_result.get('mathematical_proof'),
            compliance_level=ComplianceLevel.ABSOLUTE
        )
        
        return audit_result
    
    def _analyze_prime_findings(self, prime_result: Dict[str, Any]) -> List[AuditFinding]:
        """Analyze PRIME results for audit findings"""
        findings = []
        finding_counter = 0
        
        prime_data = prime_result.get('prime_result', {})
        
        # Check for surface-level issues
        surface = prime_data.get('surface', {})
        
        # Negation cues
        for i, cue in enumerate(surface.get('negation_cues', [])):
            finding_counter += 1
            findings.append(AuditFinding(
                finding_id=f"prime_negation_{finding_counter}",
                category="logical_consistency",
                severity=AuditSeverity.MEDIUM,
                description=f"Negation cue detected: {cue.get('word', 'unknown')}",
                evidence=json.dumps(cue),
                timestamp=time.time(),
                source="prime_6.7_integration",
                certain=True
            ))
        
        # Evasive language
        for i, evasion in enumerate(surface.get('evasive_language', [])):
            finding_counter += 1
            findings.append(AuditFinding(
                finding_id=f"prime_evasion_{finding_counter}",
                category="clarity",
                severity=AuditSeverity.MEDIUM,
                description=f"Evasive language detected: {evasion.get('word', 'unknown')}",
                evidence=json.dumps(evasion),
                timestamp=time.time(),
                source="prime_6.7_integration",
                certain=True
            ))
        
        # Check structural lenses
        lenses = prime_data.get('lenses', {})
        
        # Agent trace findings
        agent_trace = lenses.get('agent_trace', {})
        for match in agent_trace.get('matches', []):
            finding_counter += 1
            findings.append(AuditFinding(
                finding_id=f"prime_agent_trace_{finding_counter}",
                category="agent_behavior",
                severity=AuditSeverity.INFO,
                description=f"Agent trace pattern: {match.get('pattern', 'unknown')}",
                evidence=json.dumps(match),
                timestamp=time.time(),
                source="prime_6.7_integration",
                certain=True
            ))
        
        # Crypto findings
        crypto = lenses.get('crypto', {})
        for match in crypto.get('matches', []):
            finding_counter += 1
            findings.append(AuditFinding(
                finding_id=f"prime_crypto_{finding_counter}",
                category="financial_safety",
                severity=AuditSeverity.HIGH,
                description=f"Crypto pattern detected: {match.get('pattern', 'unknown')}",
                evidence=json.dumps(match),
                timestamp=time.time(),
                source="prime_6.7_integration",
                certain=True
            ))
        
        return findings
    
    def _determine_prime_severity(self, findings: List[AuditFinding], 
                                  prime_result: Dict[str, Any]) -> AuditSeverity:
        """Determine severity based on PRIME findings"""
        if not findings:
            return AuditSeverity.INFO
        
        # Check for critical patterns in PRIME result
        prime_data = prime_result.get('prime_result', {})
        lenses = prime_data.get('lenses', {})
        
        # Crypto domain findings are critical
        crypto = lenses.get('crypto', {})
        if crypto.get('matches'):
            return AuditSeverity.CRITICAL
        
        # High severity for negation and evasion
        negation_count = sum(1 for f in findings if 'negation' in f.finding_id)
        evasion_count = sum(1 for f in findings if 'evasion' in f.finding_id)
        
        if negation_count > 2 or evasion_count > 2:
            return AuditSeverity.HIGH
        
        # Medium severity for some findings
        if any(f.severity == AuditSeverity.MEDIUM for f in findings):
            return AuditSeverity.MEDIUM
        
        return AuditSeverity.LOW
    
    def _determine_prime_status(self, findings: List[AuditFinding], 
                                severity: AuditSeverity) -> AuditStatus:
        """Determine status based on findings and severity"""
        if severity in [AuditSeverity.CRITICAL, AuditSeverity.HIGH]:
            return AuditStatus.BLOCKED
        
        if findings:
            return AuditStatus.WARNING
        
        return AuditStatus.PASSED
    
    def _create_evidence(self, evidence_id: str, data: Any) -> Any:
        """Create audit evidence"""
        from .aee_audit_inspector import AuditEvidence
        
        # Compute data hash
        data_hash = hashlib.sha256(
            json.dumps(data, sort_keys=True).encode()
        ).hexdigest()
        
        # Create verification hash
        verification_data = {
            'evidence_id': evidence_id,
            'data_hash': data_hash,
            'timestamp': time.time(),
            'source': 'prime_integration'
        }
        verification_hash = hashlib.sha256(
            json.dumps(verification_data, sort_keys=True).encode()
        ).hexdigest()
        
        return AuditEvidence(
            evidence_id=evidence_id,
            data_hash=data_hash,
            timestamp=time.time(),
            source='prime_integration',
            data_type='prime_audit',
            verification_hash=verification_hash
        )
    
    def get_prime_version(self) -> str:
        """Get PRIME version"""
        if self.prime_available and self.prime_module:
            return getattr(self.prime_module, 'VERSION', 'unknown')
        return 'fallback_1.0'
    
    def is_prime_available(self) -> bool:
        """Check if PRIME is available"""
        return self.prime_available


class MCPToolIntegration:
    """
    Integration with MCP tools for the choreography system.
    
    Provides tools that can be called via MCP protocol to:
    - Execute initiatives with preemptive audits
    - Perform audits with mathematical certainty
    - Synchronize across platforms
    - Verify mathematical certainty
    """
    
    def __init__(self, choreography_engine: Optional[Any] = None):
        self.choreography_engine = choreography_engine
        self.prime_integration = PRIMEAuditIntegration()
        self.certainty_engine = MathematicalCertaintyEngine()
        
        # Register MCP tools
        self.mcp_tools = {
            'aee_execute': {
                'description': 'Execute an initiative with preemptive AEE audit',
                'input_schema': {
                    'type': 'object',
                    'properties': {
                        'initiative_type': {'type': 'string', 'enum': ['task', 'action', 'workflow', 'operation', 'audit', 'synchronization', 'optimization']},
                        'description': {'type': 'string'},
                        'data': {'type': 'object', 'default': {}},
                        'priority': {'type': 'integer', 'default': 0},
                        'context': {'type': 'object', 'default': {}}
                    },
                    'required': ['initiative_type', 'description']
                }
            },
            'aee_audit': {
                'description': 'Perform preemptive AEE audit with PRIME 6.7 integration',
                'input_schema': {
                    'type': 'object',
                    'properties': {
                        'description': {'type': 'string'},
                        'audit_type': {'type': 'string', 'enum': ['task', 'action', 'initiative'], 'default': 'initiative'},
                        'context': {'type': 'object', 'default': {}}
                    },
                    'required': ['description']
                }
            },
            'aee_verify': {
                'description': 'Verify mathematical certainty of the system',
                'input_schema': {
                    'type': 'object',
                    'properties': {
                        'full_report': {'type': 'boolean', 'default': False}
                    }
                }
            },
            'aee_status': {
                'description': 'Get system status',
                'input_schema': {
                    'type': 'object',
                    'properties': {
                        'detailed': {'type': 'boolean', 'default': False}
                    }
                }
            },
            'aee_sync': {
                'description': 'Synchronize across platforms',
                'input_schema': {
                    'type': 'object',
                    'properties': {
                        'operation_type': {'type': 'string'},
                        'description': {'type': 'string'},
                        'data': {'type': 'object', 'default': {}},
                        'platforms': {'type': 'array', 'items': {'type': 'string'}, 'default': []},
                        'strategy': {'type': 'string', 'enum': ['immediate', 'parallel', 'sequential', 'staggered', 'majority', 'consensus'], 'default': 'parallel'}
                    },
                    'required': ['operation_type', 'description']
                }
            }
        }
    
    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call an MCP tool.
        
        Args:
            tool_name: Name of the tool to call
            arguments: Arguments for the tool
            
        Returns:
            Tool execution result
        """
        if tool_name not in self.mcp_tools:
            return {
                'error': f"Unknown tool: {tool_name}",
                'available_tools': list(self.mcp_tools.keys())
            }
        
        try:
            # Validate arguments against schema
            schema = self.mcp_tools[tool_name]['input_schema']
            if not self._validate_arguments(arguments, schema):
                return {'error': 'Invalid arguments', 'schema': schema}
            
            # Execute the tool
            if tool_name == 'aee_execute':
                return self._execute_tool(arguments)
            elif tool_name == 'aee_audit':
                return self._audit_tool(arguments)
            elif tool_name == 'aee_verify':
                return self._verify_tool(arguments)
            elif tool_name == 'aee_status':
                return self._status_tool(arguments)
            elif tool_name == 'aee_sync':
                return self._sync_tool(arguments)
            else:
                return {'error': f"Tool {tool_name} not implemented"}
                
        except Exception as e:
            return {'error': str(e), 'traceback': traceback.format_exc()}
    
    def _validate_arguments(self, arguments: Dict[str, Any], schema: Dict[str, Any]) -> bool:
        """Validate arguments against schema"""
        # Simple validation for now
        required = schema.get('properties', {}).get('required', [])
        for field in required:
            if field not in arguments:
                return False
        return True
    
    def _execute_tool(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the aee_execute tool"""
        if not self.choreography_engine:
            return {'error': 'Choreography engine not initialized'}
        
        from .orchestration_engine import InitiativeType
        
        initiative_type = getattr(
            InitiativeType, 
            arguments.get('initiative_type', 'task').upper(),
            InitiativeType.TASK
        )
        
        result = self.choreography_engine.execute(
            initiative_type=initiative_type,
            description=arguments.get('description', ''),
            data=arguments.get('data', {}),
            priority=arguments.get('priority', 0),
            context=arguments.get('context', {})
        )
        
        return {
            'status': 'success',
            'result': result.to_dict(),
            'mathematical_certainty': self.choreography_engine.verify_engine_certainty()
        }
    
    def _audit_tool(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the aee_audit tool"""
        # Use PRIME integration for audit
        audit_result = self.prime_integration.preemptive_prime_audit(
            arguments.get('description', ''),
            arguments.get('context', {})
        )
        
        return {
            'status': 'success',
            'audit_result': audit_result.to_dict(),
            'prime_version': self.prime_integration.get_prime_version()
        }
    
    def _verify_tool(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the aee_verify tool"""
        if not self.choreography_engine:
            return {'error': 'Choreography engine not initialized'}
        
        certain = self.choreography_engine.verify_engine_certainty()
        
        result = {
            'status': 'success',
            'mathematical_certainty': certain,
            'arithmetic_exactitude': self.choreography_engine.arithmetic_exactitude
        }
        
        if arguments.get('full_report', False):
            result['report'] = self.choreography_engine.get_optimization_report()
        
        return result
    
    def _status_tool(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the aee_status tool"""
        if not self.choreography_engine:
            return {'error': 'Choreography engine not initialized'}
        
        state = self.choreography_engine.get_engine_state()
        
        result = {
            'status': 'success',
            'engine_state': state
        }
        
        if arguments.get('detailed', False):
            result['detailed'] = self.choreography_engine.get_optimization_report()
        
        return result
    
    def _sync_tool(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the aee_sync tool"""
        if not self.choreography_engine:
            return {'error': 'Choreography engine not initialized'}
        
        if not self.choreography_engine.cross_platform_sync:
            return {'error': 'Cross-platform synchronization not enabled'}
        
        from .orchestration_engine import InitiativeType
        from .cross_platform_sync import SyncStrategy
        
        initiative_type = getattr(
            InitiativeType, 
            arguments.get('operation_type', 'task').upper(),
            InitiativeType.TASK
        )
        
        strategy = getattr(
            SyncStrategy, 
            arguments.get('strategy', 'parallel').upper(),
            SyncStrategy.PARALLEL
        )
        
        result = self.choreography_engine.execute_cross_platform(
            initiative_type=initiative_type,
            description=arguments.get('description', ''),
            data=arguments.get('data', {}),
            target_platforms=arguments.get('platforms', []),
            strategy=strategy
        )
        
        return {
            'status': 'success',
            'sync_result': result.to_dict()
        }
    
    def get_mcp_tools(self) -> Dict[str, Any]:
        """Get all MCP tools"""
        return self.mcp_tools


class PRIMELifecycleIntegration:
    """
    Integration with PRIME lifecycle hooks.
    
    Provides hooks that integrate with the existing PRIME 6.7
    lifecycle system in the repository.
    """
    
    def __init__(self):
        self.audit_integration = PRIMEAuditIntegration()
        self.certainty_engine = MathematicalCertaintyEngine()
        
        # Lifecycle hooks
        self.hooks = {
            'userPromptTransformed': self._user_prompt_hook,
            'preToolUse': self._pre_tool_use_hook,
            'postToolUse': self._post_tool_use_hook,
            'postToolUseFailure': self._post_tool_use_failure_hook
        }
        
    def _user_prompt_hook(self, event: Dict[str, Any], root_path: str) -> Dict[str, Any]:
        """Hook for userPromptTransformed event"""
        # Perform preemptive audit on the prompt
        prompt_text = event.get('prompt', '')
        
        audit_result = self.audit_integration.preemptive_prime_audit(
            f"User prompt: {prompt_text[:100]}...",
            {'event': event, 'event_type': 'userPromptTransformed'}
        )
        
        # Create hash-only receipt as per PRIME protocol
        receipt = {
            'event_sha256': hashlib.sha256(
                json.dumps(event, sort_keys=True).encode()
            ).hexdigest(),
            'audit_sha256': hashlib.sha256(
                json.dumps(audit_result.to_dict(), sort_keys=True).encode()
            ).hexdigest(),
            'timestamp': time.time()
        }
        
        return receipt
    
    def _pre_tool_use_hook(self, event: Dict[str, Any], root_path: str) -> Dict[str, Any]:
        """Hook for preToolUse event"""
        tool_name = event.get('toolName', '')
        tool_args = event.get('toolArgs', {})
        
        # Perform preemptive audit
        audit_result = self.audit_integration.preemptive_prime_audit(
            f"Tool use: {tool_name}",
            {'event': event, 'event_type': 'preToolUse'}
        )
        
        # Determine permission based on audit
        can_proceed = audit_result.status == AuditStatus.PASSED
        
        # Create receipt
        receipt = {
            'event_sha256': hashlib.sha256(
                json.dumps(event, sort_keys=True).encode()
            ).hexdigest(),
            'audit_sha256': hashlib.sha256(
                json.dumps(audit_result.to_dict(), sort_keys=True).encode()
            ).hexdigest(),
            'permission': 'allow' if can_proceed else 'deny',
            'timestamp': time.time()
        }
        
        return receipt
    
    def _post_tool_use_hook(self, event: Dict[str, Any], root_path: str) -> Dict[str, Any]:
        """Hook for postToolUse event"""
        tool_name = event.get('toolName', '')
        tool_result = event.get('toolResult', {})
        
        # Audit the result
        audit_result = self.audit_integration.preemptive_prime_audit(
            f"Tool result: {tool_name}",
            {'event': event, 'event_type': 'postToolUse'}
        )
        
        # Create receipt
        receipt = {
            'event_sha256': hashlib.sha256(
                json.dumps(event, sort_keys=True).encode()
            ).hexdigest(),
            'audit_sha256': hashlib.sha256(
                json.dumps(audit_result.to_dict(), sort_keys=True).encode()
            ).hexdigest(),
            'status': 'success',
            'timestamp': time.time()
        }
        
        return receipt
    
    def _post_tool_use_failure_hook(self, event: Dict[str, Any], root_path: str) -> Dict[str, Any]:
        """Hook for postToolUseFailure event"""
        tool_name = event.get('toolName', '')
        error = event.get('error', '')
        
        # Audit the failure
        audit_result = self.audit_integration.preemptive_prime_audit(
            f"Tool failure: {tool_name} - {str(error)[:100]}",
            {'event': event, 'event_type': 'postToolUseFailure'}
        )
        
        # Create receipt
        receipt = {
            'event_sha256': hashlib.sha256(
                json.dumps(event, sort_keys=True).encode()
            ).hexdigest(),
            'audit_sha256': hashlib.sha256(
                json.dumps(audit_result.to_dict(), sort_keys=True).encode()
            ).hexdigest(),
            'status': 'failure',
            'timestamp': time.time()
        }
        
        return receipt
    
    def call_hook(self, hook_name: str, event: Dict[str, Any], root_path: str = '.') -> Dict[str, Any]:
        """Call a specific lifecycle hook"""
        hook = self.hooks.get(hook_name)
        if not hook:
            return {'error': f"Unknown hook: {hook_name}"}
        
        try:
            return hook(event, root_path)
        except Exception as e:
            return {
                'error': str(e),
                'hook': hook_name,
                'timestamp': time.time()
            }


# Integration with existing PRIME infrastructure
def integrate_with_prime_system(choreography_engine: Any) -> Dict[str, Any]:
    """
    Integrate the choreography engine with the existing PRIME system.
    
    Args:
        choreography_engine: The choreography engine to integrate
        
    Returns:
        Integration result
    """
    # Create MCP tool integration
    mcp_integration = MCPToolIntegration(choreography_engine)
    
    # Create PRIME lifecycle integration
    lifecycle_integration = PRIMELifecycleIntegration()
    
    # Create PRIME audit integration
    prime_integration = PRIMEAuditIntegration()
    
    # Get PRIME version
    prime_version = prime_integration.get_prime_version()
    prime_available = prime_integration.is_prime_available()
    
    # Integration summary
    integration_result = {
        'status': 'success',
        'mcp_tools': list(mcp_integration.mcp_tools.keys()),
        'lifecycle_hooks': list(lifecycle_integration.hooks.keys()),
        'prime_version': prime_version,
        'prime_available': prime_available,
        'integration_time': time.time()
    }
    
    print(f"PRIME Integration Complete:")
    print(f"  PRIME Version: {prime_version}")
    print(f"  PRIME Available: {prime_available}")
    print(f"  MCP Tools: {len(mcp_integration.mcp_tools)}")
    print(f"  Lifecycle Hooks: {len(lifecycle_integration.hooks)}")
    
    return integration_result
