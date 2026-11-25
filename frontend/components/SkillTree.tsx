'use client';

import React, { useMemo, memo } from 'react';
import ReactFlow, {
  Background,
  Controls,
  Edge,
  Node,
  MarkerType,
  ConnectionLineType,
  Handle,
  Position,
} from 'reactflow';
import dagre from 'dagre';
import 'reactflow/dist/style.css';

// [background, text, border]: green for mastered, blue for ready, grey for locked.
const COLORS: Record<string, [string, string, string]> = {
  mastered: ['#dcfce7', '#166534', '#86efac'],
  ready: ['#dbeafe', '#1e40af', '#93c5fd'],
  locked: ['#f3f4f6', '#6b7280', '#d1d5db'],
};

const StandardNode = memo(({ data }: any) => {
  const [background, color, borderColor] = COLORS[data.state] ?? COLORS.locked;
  return (
    <div
      className="px-4 py-2 shadow-md rounded-xl border-2 transition-all flex flex-col justify-center items-center text-center"
      style={{
        background,
        color,
        borderColor,
        width: '220px',
        height: '100px',
      }}
    >
      <Handle type="target" position={Position.Top} className="w-3 h-3 !bg-neutral-400" />
      <div className="font-bold text-sm leading-tight mb-1 overflow-hidden line-clamp-3">
        {data.label}
      </div>
      {data.idLabel && <div className="text-[10px] opacity-60 font-mono">{data.idLabel}</div>}
      <Handle type="source" position={Position.Bottom} className="w-3 h-3 !bg-neutral-400" />
    </div>
  );
});

StandardNode.displayName = 'StandardNode';

const nodeTypes = {
  standard: StandardNode,
};

interface SkillTreeProps {
  nodes: Node[];
  edges: Edge[];
}

const dagreGraph = new dagre.graphlib.Graph();
dagreGraph.setDefaultEdgeLabel(() => ({}));

const nodeWidth = 220;
const nodeHeight = 100;

const getLayoutedElements = (nodes: Node[], edges: Edge[]) => {
  dagreGraph.setGraph({ rankdir: 'TB' });
  nodes.forEach((node) => dagreGraph.setNode(node.id, { width: nodeWidth, height: nodeHeight }));
  edges.forEach((edge) => dagreGraph.setEdge(edge.source, edge.target));
  dagre.layout(dagreGraph);

  nodes.forEach((node) => {
    const { x, y } = dagreGraph.node(node.id);
    node.targetPosition = Position.Top;
    node.sourcePosition = Position.Bottom;
    // dagre gives the centre; React Flow anchors nodes at the top left.
    node.position = { x: x - nodeWidth / 2, y: y - nodeHeight / 2 };
  });

  return { nodes, edges };
};

export function SkillTree({ nodes: initialNodes, edges: initialEdges }: SkillTreeProps) {
  const { nodes: layoutedNodes, edges: layoutedEdges } = useMemo(() => {
    const { nodes, edges } = getLayoutedElements(initialNodes, initialEdges);
    return {
      nodes: nodes.map((n) => ({ ...n, type: 'standard' })),
      edges,
    };
  }, [initialNodes, initialEdges]);

  const styledEdges = useMemo(() => {
    return layoutedEdges.map((edge) => ({
      ...edge,
      animated: edge.data?.type === 'dependency' && !edge.data?.implicit,
      type: ConnectionLineType.SmoothStep,
      style: {
        stroke: edge.data?.implicit ? '#cbd5e1' : '#94a3b8',
        strokeWidth: 2,
        strokeDasharray: edge.data?.implicit ? '5,5' : 'none',
      },
      markerEnd: {
        type: MarkerType.ArrowClosed,
        color: edge.data?.implicit ? '#cbd5e1' : '#94a3b8',
      },
    }));
  }, [layoutedEdges]);

  return (
    <div className="h-[700px] w-full border border-neutral-200 rounded-2xl overflow-hidden bg-neutral-50">
      <ReactFlow
        nodes={layoutedNodes}
        edges={styledEdges}
        nodeTypes={nodeTypes}
        connectionLineType={ConnectionLineType.SmoothStep}
        fitView
      >
        <Background color="#cbd5e1" gap={20} />
        <Controls />
      </ReactFlow>
    </div>
  );
}
