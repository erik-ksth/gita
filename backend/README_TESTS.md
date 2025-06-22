# Agent Test Suite

This directory contains a comprehensive test suite for all agents in the Gita AI system.

## Test File: `agents_test.py`

All testing code has been moved from individual agent files to this centralized test suite to prevent tests from running in the main application flow.

## Usage

### Run All Tests

```bash
python agents_test.py
```

### Run Specific Tests

```bash
# Test prompt checker agent
python agents_test.py prompt_checker

# Test music generator agent
python agents_test.py music_generator

# Test video processor agent
python agents_test.py video_processor

# Test prompt generator agent
python agents_test.py prompt_generator

# Test orchestrator agent
python agents_test.py orchestrator

# Test agent integration
python agents_test.py integration

# Test Supabase connection
python agents_test.py supabase
```

## Available Tests

1. **prompt_checker** - Tests prompt validation and improvement functionality
2. **music_generator** - Tests music generation with Lyria API
3. **video_processor** - Tests video processing and frame extraction
4. **prompt_generator** - Tests vision analysis and prompt generation
5. **orchestrator** - Tests complete workflow integration
6. **integration** - Tests all agents can be imported and work together
7. **supabase** - Tests Supabase connection and configuration
8. **all** - Runs all tests in sequence (default)

## Test Features

- **Error Handling**: Each test includes proper error handling and informative messages
- **Import Safety**: Tests gracefully handle missing dependencies
- **Modular Design**: Individual tests can be run independently
- **Comprehensive Coverage**: Tests all major functionality of each agent
- **Real-world Scenarios**: Tests include realistic use cases and edge cases

## Dependencies

The test suite requires the same dependencies as the main application:

- All agent dependencies (google-adk, supabase, etc.)
- Environment variables configured in `.env`
- Supabase connection properly set up

## Notes

- Tests use placeholder data (like `"your-test-video-id-here"`) that should be replaced with actual test data
- Some tests may fail if dependencies are not installed or environment is not configured
- The test suite is designed to be safe to run in any environment without affecting production data
