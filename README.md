# Netlist Analysis for Circuit Performance Correlation

## Research Goal

This project aims to develop an LLM-based system that can automatically identify and explain how changes in circuit connections (netlist modifications) correlate with performance metric improvements between different circuit designs targeting the same goal.

When researchers publish multiple circuit designs for the same application (e.g., voltage references, amplifiers, etc.), they often achieve different performance metrics. Our goal is to enable an LLM to analyze two netlists and explain **what specific connection changes caused the performance improvement**.

## Problem Statement

Traditional netlist comparison approaches have limitations:
- **Direct netlist prompting**: Simply asking "what are the changes in connections" between two netlists often yields poor results
- **Graph representation**: Converting netlists to graph format for comparison hasn't significantly improved LLM understanding
- **Missing context**: Netlists alone lack the design rationale and performance context that helps explain why changes matter

## Proposed Approach

### 1. Enhanced Input Strategy
- **Full research papers** containing both netlists
- **Chunked text sections** from relevant papers
- **Performance metric summaries** alongside netlist data
- **Design methodology descriptions** that provide context

### 2. Improved Netlist Representation
explore better ways to represent netlists for LLM consumption:
- **Enhanced graph formats** with better node/edge labeling
- **Hierarchical representations** that preserve circuit structure


## Expected Outcomes

The system should be able to:
1. **Identify structural changes** between two netlists
2. **Correlate changes** with specific performance improvements
3. **Explain the design rationale** behind connection modifications
4. **Provide actionable insights** for circuit designers

## Current Status

- ✅ Basic netlist parsing and comparison framework
- ✅ Graph representation experimentation
- 🔄 Enhanced input strategies (papers + netlists)
- 🔄 Improved netlist representation formats
- ❌ LLM performance correlation analysis

## Files

- `netlist/` - Contains netlists from research papers
- `papers/` - Research papers for context
- `graph.py` - Graph representation experiments
- `difference.py` - Netlist comparison utilities
- `text2text.py` - Text processing for paper content
- `prompt.py` - LLM prompting strategies
