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

const StandardNode = memo(({ data }: any) => {
  let backgroundColor = '#f3f4f6'; // neutral-100 (locked)
  let textColor = '#6b7280'; // neutral-500
  let borderColor = '#d1d5db'; // neutral-300

  if (data.state === 'mastered') {
    backgroundColor = '#dcfce7'; // green-100
    textColor = '#166534'; // green-800
    borderColor = '#86efac'; // green-300
  } else if (data.state === 'ready') {
    backgroundColor = '#dbeafe'; // blue-100
    textColor = '#1e40af'; // blue-800
    borderColor = '#93c5fd'; // blue-300
  }

  return (
    <div
      className="px-4 py-2 shadow-md rounded-xl border-2 transition-all flex flex-col justify-center items-center text-center"
      style={{
        background: backgroundColor,
        color: textColor,
        borderColor: borderColor,
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

const getLayoutedElements = (nodes: Node[], edges: Edge[], direction = 'TB') => {
  const isHorizontal = direction === 'LR';
  dagreGraph.setGraph({ rankdir: direction });

  nodes.forEach((node) => {
    dagreGraph.setNode(node.id, { width: nodeWidth, height: nodeHeight });
  });

  edges.forEach((edge) => {
    dagreGraph.setEdge(edge.source, edge.target);
  });

  dagre.layout(dagreGraph);

  nodes.forEach((node) => {
    const nodeWithPosition = dagreGraph.node(node.id);
    node.targetPosition = isHorizontal ? ('left' as any) : ('top' as any);
    node.sourcePosition = isHorizontal ? ('right' as any) : ('bottom' as any);

    // We are shifting the dagre node position (center) to the top left, so it matches the React Flow node anchor point (top left).
    node.position = {
      x: nodeWithPosition.x - nodeWidth / 2,
      y: nodeWithPosition.y - nodeHeight / 2,
    };

    return node;
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
