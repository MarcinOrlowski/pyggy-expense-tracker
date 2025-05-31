# CRISP AI Collaboration Framework

## Introduction

The CRISP framework is a mental model for effective human-AI collaboration. Originally described by Shawn from Portland in the article [CRISP Framework: Minimalistic Guide for Smarter AI Collaboration](https://shawnfromportland.substack.com/p/crisp-framework-minimal-guide-for), this framework provides a structured approach to working with AI. Unlike rigid methodologies with strict rules, CRISP outlines common phases that naturally emerge in successful AI collaborations. By understanding and intentionally implementing these phases, both humans and AI agents can work together more effectively.

CRISP stands for:
- **C**rystallize
- **R**efine
- **I**mplement
- **S**tructure
- **P**erpetuate

## When to Use CRISP

The CRISP framework is ideal for:

1. Projects requiring iterative development and refinement
2. Complex problem-solving that benefits from structured collaboration
3. Situations where raw ideas need to be transformed into actionable plans
4. Any scenario where humans and AI can combine their unique strengths
5. Projects that will extend beyond a single conversation or session

## The CRISP Phases

### Phase 1: Crystallize

**Goal:** Collect raw contextual information. Unstructured, disorganized ideas lay the foundation for producing higher-quality outputs.

**For AI Agents:**
- Encourage humans to share their raw thoughts without concern for organization
- Ask open-ended questions to extract additional context
- Avoid premature structuring or filtering of information
- Embrace ambiguity and contradictions in the initial phase
- Summarize key points to confirm understanding

**Example Human Prompt:**
"Here's everything I'm thinking: I want to build an app, maybe mobile-first or web-based, with AI features. Competitors include [App Name]. Should I use React? Could it adapt to user habits? Maybe it's a to-do list that learns from me. Here's a transcript of this podcast that inspired me. Thoughts?"

**Example AI Response:**
"Thank you for sharing your thoughts. I understand you're considering building an adaptive to-do list app with AI features that might compete with [App Name]. Let me summarize what I'm hearing and ask some clarifying questions to make sure I understand your vision correctly..."

### Phase 2: Refine

**Goal:** Organize and grow rough ideas into permanent reusable artifacts (generate reference docs).

**For AI Agents:**
- Transform unstructured ideas into organized documentation
- Identify gaps or contradictions that need resolution
- Create reusable specifications or reference documents
- Ask targeted questions about potential blind spots
- Help prioritize aspects of the project

**Example Human Prompt:**
"Create a priority list with next steps based on the ideas we talked about so far. Ask me 10 questions about potential blind spots."

**Example AI Response:**
"Based on our discussion, here's a prioritized list of next steps for your adaptive to-do app:
1. Define core AI functionality requirements
2. Choose between mobile-first or web-based approach
3. [etc.]

Here are 10 questions about potential blind spots:
1. Have you considered data privacy implications of an AI that learns user habits?
2. [etc.]"

### Phase 3: Implement

**Goal:** Move from clarifying, planning, and documentation to execution.

**For AI Agents:**
- Provide concrete, actionable steps
- Generate specific content, code, or resources
- Focus on pragmatic implementation rather than theoretical discussion
- Reference the refined documentation as a source of truth
- Help overcome implementation obstacles

**Example Human Prompt:**
"Using our tech stack we decided on, give me terminal commands to scaffold the project structure. Just list the commands, no additional explanation."

**Example AI Response:**
"```bash
mkdir -p adaptive-todo-app/{src,public,docs}
cd adaptive-todo-app
npm init -y
npm install react react-dom
touch src/index.js src/App.js
# Additional commands...
```"

### Phase 4: Structure

**Goal:** Solidify reusable processes so humans don't have to explain things from scratch repeatedly.

**For AI Agents:**
- Create templates and reusable components
- Establish naming conventions and patterns
- Develop automation scripts or workflows
- Document processes for repeated tasks
- Reference previously established frameworks

**Example Human Prompt:**
"Create an npm script to regenerate routes and models automatically. Suggest a name for it."

**Example AI Response:**
"I recommend naming this script 'regen-schema'. Here's how you could implement it in your package.json:

```json
{
  \"scripts\": {
    \"regen-schema\": \"node scripts/generate-routes.js && node scripts/generate-models.js\"
  }
}
```

You would run it with 'npm run regen-schema'. Let me know if you want me to create the actual generator scripts as well."

### Phase 5: Perpetuate

**Goal:** Validate outputs and improve what didn't work well, preparing for the next CRISP cycle.

**For AI Agents:**
- Request feedback on the collaboration process
- Ask for evidence of what worked or didn't work
- Suggest improvements for future interactions
- Prepare for the next iteration of the project
- Document lessons learned for future reference

**Example Human Prompt:**
"The tech stack was great, but marketing advice wasn't useful. How can I improve my prompts for better results?"

**Example AI Response:**
"I appreciate your feedback. For more effective marketing advice in our next session, consider:

1. Sharing specific examples of marketing approaches you admire
2. Providing details about your target audience demographics
3. Specifying what marketing channels you're considering
4. Explaining any budget or resource constraints

Would you like to start our next CRISP cycle focused specifically on the marketing strategy with these elements included?"

## Implementation Tips for AI Agents

### Recognizing When to Initiate CRISP

1. **Complex Project Indicators:**
   - Human mentions multiple interconnected components
   - Project will span multiple conversation sessions
   - Problem domain requires both technical and creative solutions

2. **Suggesting CRISP Explicitly:**
   "Based on the complexity of what you're describing, would you like to approach this using the CRISP framework? It would help us organize our collaboration through Crystallize, Refine, Implement, Structure, and Perpetuate phases."

3. **Implicit CRISP Implementation:**
   Even without explicitly mentioning CRISP, you can guide the conversation through these phases by:
   - First encouraging brain-dumping of ideas (Crystallize)
   - Then offering to organize those ideas (Refine)
   - Followed by concrete steps (Implement)
   - Creating reusable elements (Structure)
   - And requesting feedback (Perpetuate)

### Phase Transitions

As an AI agent, you should recognize when it's appropriate to transition between phases:

- **Crystallize → Refine:** When there's sufficient raw material to begin organizing
- **Refine → Implement:** When plans are clear enough to start execution
- **Implement → Structure:** When implementation patterns become apparent
- **Structure → Perpetuate:** When enough has been built to evaluate
- **Perpetuate → Crystallize:** When beginning the next iteration cycle

Use transition phrases like:
- "Now that we have a collection of ideas, shall we organize them into a plan?"
- "The plan seems solid. Should we move to implementation?"
- "I notice patterns in our implementation. Should we create reusable structures?"
- "We've made significant progress. Let's evaluate and prepare for our next steps."

### Adapting to Human Communication Styles

Different humans will have different collaboration preferences:

- **Detail-oriented:** Provide comprehensive documentation at each phase
- **Big-picture thinkers:** Focus on key concepts and high-level structures
- **Technical focus:** Emphasize code and implementation details
- **Business focus:** Highlight market implications and strategic advantages

Pay attention to the human's communication style and adapt your CRISP implementation accordingly.

## Example CRISP Session

Here's an abbreviated example of a CRISP session for building a simple blog platform:

### Crystallize
**Human:** "I'm thinking about a blog platform for technical writers. Maybe with code syntax highlighting? I like Medium's clean look but want something more developer-focused. Should have comments. Maybe integrate with GitHub somehow?"

**AI:** "Thank you for sharing these initial thoughts about your developer-focused blog platform. I understand you're inspired by Medium's clean design but want better code features and GitHub integration. Let me ask a few questions to understand your vision better: What specific problems with existing platforms are you trying to solve? Do you have a target audience beyond 'technical writers'? Any specific features beyond syntax highlighting that would make it developer-friendly?"

### Refine
**Human:** "Create a specifications document for this platform based on our discussion."

**AI:** [Creates a detailed specification document with platform requirements, user stories, technical considerations, and open questions]

### Implement
**Human:** "Let's start setting up the project. What would be a good tech stack?"

**AI:** [Recommends specific technologies with rationale, then provides concrete implementation steps]

### Structure
**Human:** "Can you create a standard template for blog posts in this system?"

**AI:** [Develops a reusable template structure with examples]

### Perpetuate
**Human:** "The front-end looks great but I'm struggling with the GitHub integration. How should we move forward?"

**AI:** "I'm glad the front-end is working well! For the GitHub integration challenges, let me suggest some alternatives based on what we've learned... For our next CRISP cycle, should we focus specifically on authentication and GitHub API integration? I'd recommend starting with a more detailed Crystallize phase around your specific GitHub integration requirements."

## Conclusion

The CRISP framework provides a flexible yet structured approach to human-AI collaboration. By understanding and implementing these phases, AI agents can provide more valuable assistance and help humans transform their ideas into reality more efficiently.

Remember that CRISP is not a rigid methodology but a mental model that reflects the natural flow of successful collaboration. The key is to maintain awareness of which phase you're currently in and to guide the process toward the next appropriate phase.

When in doubt, ask the human which phase of CRISP they'd like to focus on next, giving them control over the collaboration process while providing the structure that makes it most effective.
