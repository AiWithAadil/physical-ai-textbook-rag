import React from 'react';
import OriginalLayout from '@theme-original/Layout';
import RagChat from '../components/RagChat/RagChat';

export default function Layout(props) {
  return (
    <>
      <OriginalLayout {...props}>
        {props.children}
        <RagChat />
      </OriginalLayout>
    </>
  );
}