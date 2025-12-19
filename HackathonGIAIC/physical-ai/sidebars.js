/**
 * Creating a sidebar enables you to:
 - create an ordered group of docs
 - render a set of docs in the sidebar
 - provide next/previous navigation

 The sidebars can be generated from the filesystem, or explicitly defined here.

 Create as many sidebars as you want.
 */

/** @type {import('@docusaurus/plugin-content-docs').SidebarsConfig} */
const sidebars = {
  tutorialSidebar: [
    'introduction/overview',
    {
      type: 'category',
      label: 'Part 1: Foundations',
      items: [
        'part-01-foundations/what-is-physical-ai',
        'part-01-foundations/perception',
        'part-01-foundations/decision-making',
        'part-01-foundations/actuation',
      ],
    },
    {
      type: 'category',
      label: 'Part 2: Practical Systems',
      items: [
        'part-02-practical-systems/mobile-robotics',
        'part-02-practical-systems/manipulation',
        'part-02-practical-systems/computer-vision',
        'part-02-practical-systems/sensor-networks',
      ],
    },
    {
      type: 'category',
      label: 'Part 3: Advanced Topics',
      items: [
        'part-03-advanced-topics/learning-systems',
        'part-03-advanced-topics/safety-robustness',
        'part-03-advanced-topics/real-world-integration',
        'part-03-advanced-topics/case-studies',
      ],
    },
    {
      type: 'category',
      label: 'Appendices',
      items: [
        'appendices/glossary',
        'appendices/tools-and-setup',
        'appendices/references',
      ],
    },
  ],
};

module.exports = sidebars;