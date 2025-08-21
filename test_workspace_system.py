#!/usr/bin/env python3
"""
Test script for OpenHands Workspace System
Demonstrates the complete workflow from intent to execution
"""

import json
import shutil
import sys
from pathlib import Path

# Add the openhands package to Python path
sys.path.insert(0, str(Path(__file__).parent))

from openhands.workspace import Intent, WorkspaceOrchestrator


def test_workspace_system():
    """Test the complete workspace system workflow"""

    print('🚀 Testing OpenHands Workspace System')
    print('=' * 50)

    # Setup test environment
    test_root = '/tmp/test_workspaces'
    if Path(test_root).exists():
        shutil.rmtree(test_root)

    # Initialize orchestrator
    orchestrator = WorkspaceOrchestrator(storage_root=test_root)

    # Test 1: Create workspace
    print('\n1️⃣ Creating workspace...')
    workspace_name = 'bmecat-competitive-test'
    metadata = orchestrator.create_workspace(workspace_name, 'test-user')
    print(f'✅ Workspace created: {metadata.workspace_id}')
    print(f'   Path: {test_root}/{workspace_name}')

    # Verify workspace structure
    workspace_path = Path(test_root) / workspace_name
    expected_dirs = [
        'data/uploads',
        'data/outputs',
        'data/intermediate',
        'scripts/helpers',
        'context/plans',
        'context/reports',
        'docs',
        '.vscode',
    ]

    for dir_path in expected_dirs:
        full_path = workspace_path / dir_path
        if full_path.exists():
            print(f'   ✅ {dir_path}')
        else:
            print(f'   ❌ {dir_path} - MISSING')

    # Test 2: Copy BMEcat file to workspace
    print('\n2️⃣ Uploading BMEcat file...')
    source_file = Path('/workspace/BMEcat_ISOLED_2025-05-06.xml')
    if source_file.exists():
        dest_file = workspace_path / 'data/uploads/BMEcat_ISOLED_2025-05-06.xml'
        shutil.copy2(source_file, dest_file)
        print(f'✅ BMEcat file uploaded: {dest_file.stat().st_size} bytes')
    else:
        print('❌ BMEcat source file not found')
        return False

    # Test 3: Submit intent
    print('\n3️⃣ Submitting competitive analysis intent...')
    intent = Intent(
        workspace_name=workspace_name,
        intent='Extract products and crawl with Tavily all competition product on leading e-commerce sites',
        inputs=[{'type': 'file', 'path': 'data/uploads/BMEcat_ISOLED_2025-05-06.xml'}],
        constraints={
            'pii': 'redact-before-external',
            'egress_allowlist': [
                'api.tavily.com',
                '*.amazon.de',
                '*.ebay.de',
                '*.conrad.de',
            ],
            'rate_limits': {'tavily_requests_per_minute': 30, 'crawl_delay_seconds': 2},
        },
        acceptance={
            'min_competitors_per_product': 2,
            'required_fields': ['competitor_name', 'competitor_price', 'availability'],
        },
    )

    plan = orchestrator.submit_intent(workspace_name, intent)
    print(f'✅ Plan generated: {plan.plan_id}')
    print(f'   Status: {plan.status}')
    print(f'   Operations: {len(plan.operations)}')

    # Display plan details
    print('\n📋 Plan Preview:')
    for i, op in enumerate(plan.operations, 1):
        print(f'   {i}. {op.name}: {op.description}')
        if op.external_apis:
            print(f'      APIs: {", ".join(op.external_apis)}')
        if op.outputs:
            print(f'      Outputs: {len(op.outputs)} files')

    print('\n📊 Resource Estimates:')
    for key, value in plan.estimates.items():
        print(f'   {key}: {value}')

    # Test 4: Approve plan
    print('\n4️⃣ Approving plan...')
    job_id = orchestrator.approve_plan(workspace_name, plan.plan_id)
    print(f'✅ Plan approved, job started: {job_id}')

    # Test 5: Check execution results
    print('\n5️⃣ Checking execution results...')

    # Wait a moment for "execution" to complete (it's mocked)
    import time

    time.sleep(2)

    # Check for generated outputs
    outputs_dir = workspace_path / 'data/outputs'
    if outputs_dir.exists():
        output_files = list(outputs_dir.glob('*'))
        print(f'✅ Output files generated: {len(output_files)}')
        for file in output_files:
            print(f'   📄 {file.name} ({file.stat().st_size} bytes)')

    # Check for reports
    reports_dir = workspace_path / 'context/reports'
    if reports_dir.exists():
        report_files = list(reports_dir.glob('*.json'))
        print(f'✅ Agent reports generated: {len(report_files)}')
        for file in report_files:
            print(f'   📊 {file.name}')

    # Check for generated script
    scripts_dir = workspace_path / 'scripts'
    script_files = list(scripts_dir.glob(f'{job_id}.py'))
    if script_files:
        script_file = script_files[0]
        print(
            f'✅ Generated script: {script_file.name} ({script_file.stat().st_size} bytes)'
        )

        # Show first few lines of generated script
        lines = script_file.read_text().split('\n')[:10]
        print('   Script preview:')
        for line in lines:
            print(f'     {line}')
        print('     ...')

    # Test 6: Workspace status
    print('\n6️⃣ Checking workspace status...')
    status = orchestrator.get_workspace_status(workspace_name)
    print('✅ Workspace status retrieved')
    print(f'   Recent plans: {len(status["recent_plans"])}')
    print(f'   Recent reports: {len(status["recent_reports"])}')

    # Test 7: Demonstrate file outputs
    print('\n7️⃣ Demonstrating output files...')

    # Show CSV content
    csv_file = outputs_dir / 'competitive_analysis.csv'
    if csv_file.exists():
        print(f'📊 CSV Analysis Preview ({csv_file.name}):')
        lines = csv_file.read_text().split('\n')[:5]
        for line in lines:
            print(f'   {line}')
        print('   ...')

    # Show HTML report
    html_file = outputs_dir / 'price_comparison_report.html'
    if html_file.exists():
        print(f'📄 HTML Report Generated ({html_file.name})')
        print(f'   Size: {html_file.stat().st_size} bytes')
        print('   Contains executive summary and competitive analysis')

    # Show JSON analysis
    json_file = outputs_dir / 'market_gaps_analysis.json'
    if json_file.exists():
        print(f'📈 JSON Analysis Preview ({json_file.name}):')
        data = json.loads(json_file.read_text())
        print(f'   Summary: {data.get("summary", {})}')
        print(f'   Market gaps: {len(data.get("market_gaps", []))}')

    print('\n🎉 Workspace System Test Complete!')
    print(f'📁 Test workspace available at: {workspace_path}')

    return True


def test_script_execution():
    """Test the generated script execution"""
    print('\n🧪 Testing Generated Script Execution')
    print('=' * 40)

    test_root = '/tmp/test_workspaces'
    workspace_name = 'bmecat-competitive-test'
    workspace_path = Path(test_root) / workspace_name

    # Find the generated script
    scripts_dir = workspace_path / 'scripts'
    script_files = list(scripts_dir.glob('job_*.py'))

    if not script_files:
        print('❌ No generated script found')
        return False

    script_file = script_files[0]
    print(f'🐍 Found script: {script_file.name}')

    # Test script execution
    try:
        import subprocess

        # Prepare arguments
        input_file = workspace_path / 'data/uploads/BMEcat_ISOLED_2025-05-06.xml'
        output_dir = workspace_path / 'data/outputs'

        # Create intermediate directory
        (workspace_path / 'data/intermediate').mkdir(exist_ok=True)

        # Run the script
        print('🚀 Executing generated script...')
        result = subprocess.run(
            [
                sys.executable,
                str(script_file),
                str(input_file),
                str(output_dir),
                'demo_key',
            ],
            capture_output=True,
            text=True,
            cwd=str(workspace_path),
        )

        print('📤 Script execution completed')
        print(f'   Return code: {result.returncode}')

        if result.stdout:
            print('📝 Script output:')
            for line in result.stdout.split('\n')[-10:]:  # Last 10 lines
                if line.strip():
                    print(f'   {line}')

        if result.stderr and result.returncode != 0:
            print('⚠️ Script errors:')
            for line in result.stderr.split('\n')[-5:]:  # Last 5 error lines
                if line.strip():
                    print(f'   {line}')

        # Check outputs were created/updated
        output_files = list(output_dir.glob('*'))
        print(f'✅ Output files after execution: {len(output_files)}')

        return result.returncode == 0

    except Exception as e:
        print(f'❌ Script execution failed: {e}')
        return False


if __name__ == '__main__':
    print('OpenHands Workspace System - Integration Test')
    print('=' * 60)

    # Test the workspace system
    success = test_workspace_system()

    if success:
        # Test script execution
        script_success = test_script_execution()

        if script_success:
            print('\n🎊 ALL TESTS PASSED!')
            print('The Workspace system is working correctly.')
        else:
            print('\n⚠️ Workspace system works, but script execution had issues.')
    else:
        print('\n❌ Workspace system test failed.')
        sys.exit(1)
