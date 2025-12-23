import React from 'react';
import ComponentCreator from '@docusaurus/ComponentCreator';

export default [
  {
    path: '/__docusaurus/debug',
    component: ComponentCreator('/__docusaurus/debug', 'fac'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/config',
    component: ComponentCreator('/__docusaurus/debug/config', 'ad8'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/content',
    component: ComponentCreator('/__docusaurus/debug/content', 'e70'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/globalData',
    component: ComponentCreator('/__docusaurus/debug/globalData', 'b2e'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/metadata',
    component: ComponentCreator('/__docusaurus/debug/metadata', '02a'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/registry',
    component: ComponentCreator('/__docusaurus/debug/registry', 'ddc'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/routes',
    component: ComponentCreator('/__docusaurus/debug/routes', 'ab4'),
    exact: true
  },
  {
    path: '/',
    component: ComponentCreator('/', '50d'),
    routes: [
      {
        path: '/',
        component: ComponentCreator('/', '134'),
        exact: true
      },
      {
        path: '/appendices/glossary',
        component: ComponentCreator('/appendices/glossary', '5fb'),
        exact: true,
        sidebar: "tutorialSidebar"
      },
      {
        path: '/appendices/references',
        component: ComponentCreator('/appendices/references', 'c71'),
        exact: true,
        sidebar: "tutorialSidebar"
      },
      {
        path: '/appendices/tools-and-setup',
        component: ComponentCreator('/appendices/tools-and-setup', '614'),
        exact: true,
        sidebar: "tutorialSidebar"
      },
      {
        path: '/introduction/overview',
        component: ComponentCreator('/introduction/overview', '1b0'),
        exact: true,
        sidebar: "tutorialSidebar"
      },
      {
        path: '/part-01-foundations/actuation',
        component: ComponentCreator('/part-01-foundations/actuation', '08d'),
        exact: true,
        sidebar: "tutorialSidebar"
      },
      {
        path: '/part-01-foundations/decision-making',
        component: ComponentCreator('/part-01-foundations/decision-making', '2f8'),
        exact: true,
        sidebar: "tutorialSidebar"
      },
      {
        path: '/part-01-foundations/perception',
        component: ComponentCreator('/part-01-foundations/perception', 'a1c'),
        exact: true,
        sidebar: "tutorialSidebar"
      },
      {
        path: '/part-01-foundations/what-is-physical-ai',
        component: ComponentCreator('/part-01-foundations/what-is-physical-ai', '986'),
        exact: true,
        sidebar: "tutorialSidebar"
      },
      {
        path: '/part-02-practical-systems/computer-vision',
        component: ComponentCreator('/part-02-practical-systems/computer-vision', '83b'),
        exact: true,
        sidebar: "tutorialSidebar"
      },
      {
        path: '/part-02-practical-systems/manipulation',
        component: ComponentCreator('/part-02-practical-systems/manipulation', '6c0'),
        exact: true,
        sidebar: "tutorialSidebar"
      },
      {
        path: '/part-02-practical-systems/mobile-robotics',
        component: ComponentCreator('/part-02-practical-systems/mobile-robotics', '639'),
        exact: true,
        sidebar: "tutorialSidebar"
      },
      {
        path: '/part-02-practical-systems/sensor-networks',
        component: ComponentCreator('/part-02-practical-systems/sensor-networks', 'eec'),
        exact: true,
        sidebar: "tutorialSidebar"
      },
      {
        path: '/part-03-advanced-topics/case-studies',
        component: ComponentCreator('/part-03-advanced-topics/case-studies', 'b35'),
        exact: true,
        sidebar: "tutorialSidebar"
      },
      {
        path: '/part-03-advanced-topics/learning-systems',
        component: ComponentCreator('/part-03-advanced-topics/learning-systems', '5d2'),
        exact: true,
        sidebar: "tutorialSidebar"
      },
      {
        path: '/part-03-advanced-topics/real-world-integration',
        component: ComponentCreator('/part-03-advanced-topics/real-world-integration', 'dd4'),
        exact: true,
        sidebar: "tutorialSidebar"
      },
      {
        path: '/part-03-advanced-topics/safety-robustness',
        component: ComponentCreator('/part-03-advanced-topics/safety-robustness', '364'),
        exact: true,
        sidebar: "tutorialSidebar"
      }
    ]
  },
  {
    path: '*',
    component: ComponentCreator('*'),
  },
];
