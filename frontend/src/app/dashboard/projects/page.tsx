"use client";

import React from 'react';
import { KanbanBoard } from '@/components/projects/KanbanBoard';

export default function ProjectsPage() {
  return (
    <div className="h-[calc(100vh-8rem)]">
      <KanbanBoard />
    </div>
  );
}
